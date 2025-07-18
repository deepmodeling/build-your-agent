from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command

from open_deep_research.state import (
    ReportStateInput,
    ReportStateOutput,
    Sections,
    ReportState,
    SectionState,
    SectionOutputState,
    Queries,
    Feedback
)

from open_deep_research.prompts import (
    report_planner_query_writer_instructions,
    report_planner_instructions,
    query_writer_instructions, 
    section_writer_instructions,
    final_section_writer_instructions,
    section_grader_instructions,
    section_writer_inputs
)

from open_deep_research.configuration import WorkflowConfiguration
from open_deep_research.utils import (
    format_sections, 
    get_config_value, 
    get_search_params, 
    select_and_execute_search,
    get_today_str
)
import requests
import json
from typing import Any, List, Optional, Type, Sequence

# LangChain 核心类
from langchain_core.runnables import Runnable
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.prompts import ChatPromptTemplate
# 使用 langchain-core 捆绑的 Pydantic v1，以保证最大兼容性
from pydantic import BaseModel, Field

class CustomChatGemini(BaseChatModel):
    """
    一个完全自定义的 ChatModel，通过实现 bind_tools，
    并正确构建 tools 和 tool_config 请求体，
    来兼容 LangChain 的 with_structured_output。
    """
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.7
    
    # 这个属性用于存储绑定后的工具定义，在非结构化调用时为 None
    bound_tools: Optional[List[dict]] = None

    def bind_tools(
        self,
        tools: Sequence[Type[BaseModel]],
        **kwargs: Any,
    ) -> Runnable[Any, Any]:
        """
        此方法由 LangChain 的 .with_structured_output() 调用。
        它的职责是接收 Pydantic 模型，将其转换为 Gemini API 需要的格式，
        然后返回一个绑定了这些工具的新模型实例。
        """
        # 因为 with_structured_output 只会传递一个模型，我们取第一个
        if not tools:
            return self # 如果没有工具，返回自身
        
        model_class = tools[0]
  
        
        # 创建当前模型的一个新副本，并将准备好的工具定义绑定到它上面
        self.bound_tools =  json.dumps(model_class.model_json_schema(), indent=2, ensure_ascii=False)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        这个核心方法会检查模型是否绑定了工具，
        如果绑定了，就构建一个包含 'tools' 和 'tool_config' 的请求，
        并解析 'functionCall' 响应。
        """
        # a. 转换消息

        api_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage): role = "user"
            elif isinstance(msg, AIMessage): role = "model"
            elif isinstance(msg, SystemMessage): role = "user"
            else: raise ValueError(f"不支持的消息类型: {type(msg)}")
            api_messages.append({"role": role, "parts": [{"text": msg.content}]})

        # b. 准备请求 URL 和 Headers
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json",
                   "x-goog-api-key": self.api_key}

        # c. 准备基础的请求体
        data = {
            "contents": api_messages,
            "generationConfig": {"temperature": self.temperature,
                                 
                                 }
        }

        # d. [关键] 检查是否需要添加工具信息
        if self.bound_tools:
            print("检测到绑定的工具，正在构建 tool_config 和 tools 请求...")
            # 将绑定好的工具定义添加到请求体
            data["generationConfig"]["response_mime_type"] = "application/json"
            data["generationConfig"]["response_json_schema"] = json.loads(self.bound_tools)
            

        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        # f. 解析响应
        try:
            tokens = response_data['candidates'][0]['content']['parts'][0]['text']

        except (KeyError, IndexError) as e:
            raise ValueError(f"无法从API响应中解析内容: {e}\n响应: {response_data}")

        ai_message = AIMessage(content=tokens,
            additional_kwargs={},  # Used to add additional payload (e.g., function calling request)
            response_metadata={  # Use for response metadata
                "time_in_seconds": 3,
            },
            )
        generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """返回一个唯一的类型字符串，表明这是我们的自定义模型。"""
        return "custom_chat_gemini_final"
    
    def with_structured_output(
        self,   
        schema: Type[BaseModel],):
        self.bind_tools([schema])



## Nodes -- 

async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """Generate the initial report plan with sections.
    
    This node:
    1. Gets configuration for the report structure and search parameters
    2. Generates search queries to gather context for planning
    3. Performs web searches using those queries
    4. Uses an LLM to generate a structured plan with sections
    
    Args:
        state: Current graph state containing the report topic
        config: Configuration for models, search APIs, etc.
        
    Returns:
        Dict containing the generated sections
    """

    # Inputs
    topic = state["topic"]

    # Get list of feedback on the report plan
    feedback_list = state.get("feedback_on_report_plan", [])

    # Concatenate feedback on the report plan into a single string
    feedback = " /// ".join(feedback_list) if feedback_list else ""

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)
    report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries
    search_api = get_config_value(configurable.search_api)
    search_api_config = configurable.search_api_config or {}  # Get the config dict, default to empty
    params_to_pass = get_search_params(search_api, search_api_config)  # Filter parameters

    # Convert JSON object to string if necessary
    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    # Set writer model (model used for query writing)
    writer_model = get_config_value(configurable.writer_model)
    base_url = get_config_value(configurable.base_url)
    api_key = get_config_value(configurable.api_key)
    writer_model_kwargs = get_config_value(configurable.writer_model_kwargs or {})
    # writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider, model_kwargs=writer_model_kwargs) 



    structured_llm = CustomChatGemini(
        base_url=base_url,  # 你的代理地址
        api_key=api_key,
        model=writer_model,
    )


    structured_llm.with_structured_output(Queries)
    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic,
        report_organization=report_structure,
        number_of_queries=number_of_queries,
        today=get_today_str()
    )

    # Generate queries  
    results = structured_llm.invoke([SystemMessage(content=system_instructions_query),
                                     HumanMessage(content="Generate search queries that will help with planning the sections of the report.")])
    results = json.loads(results.content)
    # Web search
    query_list = [query["search_query"] for query in results["queries"]]

    # Search the web with parameters
    source_str = await select_and_execute_search(search_api, query_list, params_to_pass)

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(topic=topic, report_organization=report_structure, context=source_str, feedback=feedback)

    # Set the planner
    planner_model = get_config_value(configurable.planner_model)
    api_key = get_config_value(configurable.api_key)
    base_url = get_config_value(configurable.base_url)
    planner_model_kwargs = get_config_value(configurable.planner_model_kwargs or {})

    # Report planner instructions
    planner_message = """Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. 
                        Each section must have: name, description, research, and content fields."""

    # Run the planner
    if planner_model == "claude-3-7-sonnet-latest":
        # Allocate a thinking budget for claude-3-7-sonnet-latest as the planner model
        # planner_llm = init_chat_model(model=planner_model, 
        #                               model_provider=planner_provider, 
        #                               max_tokens=20_000, 
        #                               thinking={"type": "enabled", "budget_tokens": 16_000})

        planner_llm = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=planner_model,
        )

    else:
        planner_llm = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=planner_model,
        )

    # Generate the report sections
    planner_llm.with_structured_output(Sections)
    report_sections = planner_llm.invoke([SystemMessage(content=system_instructions_sections),
                                             HumanMessage(content=planner_message)])
    report_sections = json.loads(report_sections.content)
    # Get sections
    sections = report_sections["sections"]

    return {"sections": sections}

def human_feedback(state: ReportState, config: RunnableConfig) -> Command[Literal["generate_report_plan","build_section_with_web_research"]]:
    """Get human feedback on the report plan and route to next steps.
    
    This node:
    1. Formats the current report plan for human review
    2. Gets feedback via an interrupt
    3. Routes to either:
       - Section writing if plan is approved
       - Plan regeneration if feedback is provided
    
    Args:
        state: Current graph state with sections to review
        config: Configuration for the workflow
        
    Returns:
        Command to either regenerate plan or start section writing
    """

    # Get sections
    topic = state["topic"]
    sections = state['sections']
    # sections_str = "\n\n".join(
    #     f"Section: { section["name"] }\n"
    #     f"Description: {section["description"]}\n"
    #     f"Research needed: {'Yes' if section["research"] else 'No'}\n"
    #     for section in sections
    # )

    # # Get feedback on the report plan from interrupt
    # interrupt_message = f"""Please provide feedback on the following report plan. 
    #                     \n\n{sections_str}\n
    #                     \nDoes the report plan meet your needs?\nPass 'true' to approve the report plan.\nOr, provide feedback to regenerate the report plan:"""
    
    # feedback = interrupt(interrupt_message)
    feedback = True  # For testing purposes, we assume the user approves the report plan
    # If the user approves the report plan, kick off section writing
    if isinstance(feedback, bool) and feedback is True:
        # Treat this as approve and kick off section writing
        return Command(goto=[
            Send("build_section_with_web_research", {"topic": topic, "section": s, "search_iterations": 0}) 
            for s in sections 
            if s["research"]
        ])
    
    # If the user provides feedback, regenerate the report plan 
    elif isinstance(feedback, str):
        # Treat this as feedback and append it to the existing list
        return Command(goto="generate_report_plan", 
                       update={"feedback_on_report_plan": [feedback]})
    else:
        raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")
    
async def generate_queries(state: SectionState, config: RunnableConfig):
    """Generate search queries for researching a specific section.
    
    This node uses an LLM to generate targeted search queries based on the 
    section topic and description.
    
    Args:
        state: Current state containing section details
        config: Configuration including number of queries to generate
        
    Returns:
        Dict containing the generated search queries
    """

    # Get state 
    topic = state["topic"]
    section = state["section"]

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Generate queries 
    writer_model = get_config_value(configurable.writer_model)
    base_url = get_config_value(configurable.base_url)
    api_key = get_config_value(configurable.api_key)
    writer_model_kwargs = get_config_value(configurable.writer_model_kwargs or {})
    # writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider, model_kwargs=writer_model_kwargs) 

    structured_llm = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=writer_model,
        )


    structured_llm.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(topic=topic, 
                                                           section_topic=section["description"], 
                                                           number_of_queries=number_of_queries,
                                                           today=get_today_str())

    # Generate queries  
    queries = structured_llm.invoke([SystemMessage(content=system_instructions),
                                     HumanMessage(content="Generate search queries on the provided topic.")])
    queries = json.loads(queries.content)
    return {"search_queries": queries["queries"]}

async def search_web(state: SectionState, config: RunnableConfig):
    """Execute web searches for the section queries.
    
    This node:
    1. Takes the generated queries
    2. Executes searches using configured search API
    3. Formats results into usable context
    
    Args:
        state: Current state with search queries
        config: Search API configuration
        
    Returns:
        Dict with search results and updated iteration count
    """

    # Get state
    search_queries = state["search_queries"]

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)
    search_api = get_config_value(configurable.search_api)
    search_api_config = configurable.search_api_config or {}  # Get the config dict, default to empty
    params_to_pass = get_search_params(search_api, search_api_config)  # Filter parameters

    # Web search
    query_list = [query["search_query"] for query in search_queries]

    # Search the web with parameters
    source_str = await select_and_execute_search(search_api, query_list, params_to_pass)

    return {"source_str": source_str, "search_iterations": state["search_iterations"] + 1}

async def write_section(state: SectionState, config: RunnableConfig) -> Command[Literal[END, "search_web"]]:
    """Write a section of the report and evaluate if more research is needed.
    
    This node:
    1. Writes section content using search results
    2. Evaluates the quality of the section
    3. Either:
       - Completes the section if quality passes
       - Triggers more research if quality fails
    
    Args:
        state: Current state with search results and section info
        config: Configuration for writing and evaluation
        
    Returns:
        Command to either complete section or do more research
    """

    # Get state 
    topic = state["topic"]
    section = state["section"]
    source_str = state["source_str"]

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)

    # Format system instructions
    section_writer_inputs_formatted = section_writer_inputs.format(topic=topic, 
                                                             section_name=section["name"], 
                                                             section_topic=section["description"], 
                                                             context=source_str, 
                                                             section_content=section["content"])

    # Generate section  
    writer_model = get_config_value(configurable.writer_model)
    api_key = get_config_value(configurable.api_key)
    base_url = get_config_value(configurable.base_url)
    writer_model_kwargs = get_config_value(configurable.writer_model_kwargs or {})
    # writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider, model_kwargs=writer_model_kwargs) 

    writer_model = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=writer_model,
        )


    section_content = writer_model.invoke([SystemMessage(content=section_writer_instructions),
                                           HumanMessage(content=section_writer_inputs_formatted)])
    # Write content to the section object  
    section["content"] = section_content.content

    # Grade prompt 
    section_grader_message = ("Grade the report and consider follow-up questions for missing information. "
                              "If the grade is 'pass', return empty strings for all follow-up queries. "
                              "If the grade is 'fail', provide specific search queries to gather missing information.")
    
    section_grader_instructions_formatted = section_grader_instructions.format(topic=topic, 
                                                                               section_topic=section["description"],
                                                                               section=section["content"], 
                                                                               number_of_follow_up_queries=configurable.number_of_queries)

    # Use planner model for reflection
    planner_model = get_config_value(configurable.planner_model)
    api_key = get_config_value(configurable.api_key)
    base_url = get_config_value(configurable.base_url)
    planner_model_kwargs = get_config_value(configurable.planner_model_kwargs or {})

    if planner_model == "claude-3-7-sonnet-latest":
        # Allocate a thinking budget for claude-3-7-sonnet-latest as the planner model
        # reflection_model = init_chat_model(model=planner_model, 
        #                                    model_provider=planner_provider, 
        #                                    max_tokens=20_000, 
        #                                    thinking={"type": "enabled", "budget_tokens": 16_000}).with_structured_output(Feedback)

        reflection_model = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=planner_model,
        )

        reflection_model.with_structured_output(Feedback)
        

    else:
        # reflection_model = init_chat_model(model=planner_model, 
        #                                    model_provider=planner_provider, model_kwargs=planner_model_kwargs).with_structured_output(Feedback)
        reflection_model = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=planner_model,
        )


        reflection_model.with_structured_output(Feedback)
        
    # Generate feedback
    feedback = reflection_model.invoke([SystemMessage(content=section_grader_instructions_formatted),
                                        HumanMessage(content=section_grader_message)])
    feedback = json.loads(feedback.content)
    # If the section is passing or the max search depth is reached, publish the section to completed sections 
    if feedback["grade"] == "pass" or state["search_iterations"] >= configurable.max_search_depth:
        # Publish the section to completed sections 
        update = {"completed_sections": [section]}
        if configurable.include_source_str:
            update["source_str"] = source_str
        return Command(update=update, goto=END)

    # Update the existing section with new content and update search queries
    else:
        return Command(
            update={"search_queries": feedback["follow_up_queries"], "section": section},
            goto="search_web"
        )
    
async def write_final_sections(state: SectionState, config: RunnableConfig):
    """Write sections that don't require research using completed sections as context.
    
    This node handles sections like conclusions or summaries that build on
    the researched sections rather than requiring direct research.
    
    Args:
        state: Current state with completed sections as context
        config: Configuration for the writing model
        
    Returns:
        Dict containing the newly written section
    """

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)

    # Get state 
    topic = state["topic"]
    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]
    
    # Format system instructions
    system_instructions = final_section_writer_instructions.format(topic=topic, section_name=section["name"], section_topic=section["description"], context=completed_report_sections)

    # Generate section  
    writer_model = get_config_value(configurable.writer_model)
    base_url = get_config_value(configurable.base_url)
    api_key = get_config_value(configurable.api_key)
    writer_model_kwargs = get_config_value(configurable.writer_model_kwargs or {})
    # writer_model = init_chat_model(model=writer_model_name, model_provider=writer_provider, model_kwargs=writer_model_kwargs) 

    writer_model = CustomChatGemini(
            base_url=base_url,  # 你的代理地址
            api_key=api_key,
            model=writer_model,
        )


        
    section_content = writer_model.invoke([SystemMessage(content=system_instructions),
                                           HumanMessage(content="Generate a report section based on the provided sources.")])
    

    # Write content to section 
    s = section_content.content
    section["content"] = s
    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def gather_completed_sections(state: ReportState):
    """Format completed sections as context for writing final sections.
    
    This node takes all completed research sections and formats them into
    a single context string for writing summary sections.
    
    Args:
        state: Current state with completed sections
        
    Returns:
        Dict with formatted sections as context
    """

    # List of completed sections
    completed_sections = state["completed_sections"]

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"report_sections_from_research": completed_report_sections}

def compile_final_report(state: ReportState, config: RunnableConfig):
    """Compile all sections into the final report.
    
    This node:
    1. Gets all completed sections
    2. Orders them according to original plan
    3. Combines them into the final report
    
    Args:
        state: Current state with all completed sections
        
    Returns:
        Dict containing the complete report
    """

    # Get configuration
    configurable = WorkflowConfiguration.from_runnable_config(config)

    # Get sections
    sections = state["sections"]
    completed_sections = {s["name"]: s["content"] for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section["content"] = completed_sections[section["name"]]

    # Compile final report
    all_sections = "\n\n".join([s["content"] for s in sections])

    if configurable.include_source_str:
        return {"final_report": all_sections, "source_str": state["source_str"]}
    else:
        return {"final_report": all_sections}

def initiate_final_section_writing(state: ReportState):
    """Create parallel tasks for writing non-research sections.
    
    This edge function identifies sections that don't need research and
    creates parallel writing tasks for each one.
    
    Args:
        state: Current state with all sections and research context
        
    Returns:
        List of Send commands for parallel section writing
    """

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send("write_final_sections", {"topic": state["topic"], "section": s, "report_sections_from_research": state["report_sections_from_research"]}) 
        for s in state["sections"] 
        if not s["research"]
    ]

# Report section sub-graph -- 

# Add nodes 
section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

# Add edges
section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")

# Outer graph for initial report plan compiling results from each section -- 

# Add nodes
builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput, config_schema=WorkflowConfiguration)
builder.add_node("generate_report_plan", generate_report_plan)
builder.add_node("human_feedback", human_feedback)
builder.add_node("build_section_with_web_research", section_builder.compile())
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)
builder.add_node("compile_final_report", compile_final_report)

# Add edges
builder.add_edge(START, "generate_report_plan")
builder.add_edge("generate_report_plan", "human_feedback")
builder.add_edge("build_section_with_web_research", "gather_completed_sections")
builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
builder.add_edge("write_final_sections", "compile_final_report")
builder.add_edge("compile_final_report", END)

graph = builder.compile()

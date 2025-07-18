# Import required modules and initialize the builder from open_deep_research
import uuid  
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.graph import builder
import DPA_subagent
import os

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
# Define report structure template and configure the research workflow
# This sets parameters for models, search tools, and report organization

REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:
# {{Title}}

## 1. Variable Introduction
- **x₁:** <!-- physical/biological meaning, units, measurement context -->
- **x₂:** <!-- physical/biological meaning, units, measurement context -->
- **…**
- **y (target):** <!-- meaning of the function to be regressed -->

---

## 2. Background Equations
| Equation Name | Mathematical Form | Brief Description |
| ------------- | ----------------- | ----------------- |
|               |                   |                   |
|               |                   |                   |

---

## 3. Physically Motivated Functional Terms
- <!-- item -->
- <!-- item -->
- <!-- item -->

---

## 4. Recommended Unary Operators
- **Include:** <!-- list operators with justification -->
- **Exclude:** <!-- list operators with justification -->

---

## 5. Summary
- <!-- concise recap of key insights -->
- **Final list of endorsed unary operators:** <!-- list -->

"""


task="""
\n
Your task is to write a report on the user-provided topic.

Read the user’s problem statement and any accompanying data descriptions, perform targeted literature/web searches as needed, and produce a prior-informed technical report with the exact section titles and ordering shown below.

Report Structure
	1.	Variable Introduction
• For each variable x₁, x₂, … (and the target y), state its physical or biological meaning, units (if given), and measurement context.
	2.	Background Equations
•	Conduct an in-depth search to identify multiple canonical or widely cited governing equations relevant to the user’s system.
•	For each equation, provide:
•	The full mathematical expression
•	A one-sentence description of its functional role in modeling the system dynamics
	3.	Physically Motivated Functional Terms
• Extract from the equations in §2 the most common physically meaningful terms.
• Explain briefly why each term frequently appears in this class of models.
	4.	Recommended Unary Operators
• Based on §§2-3, recommend which unary operators  should be included or excluded in the symbolic-regression search space.
• Justify each recommendation with concrete references or empirical rationale—avoid speculation.
    5.	Summary
• Concisely recap key insights and restate the final list of endorsed unary operators.

The user's topic is:
{topic}
"""

# Define research topic about Model Context Protocol
# Run the graph workflow until first interruption (waiting for user feedback)

async def deepresearch_agent(topic):
   # Configuration option 3: Use OpenAI o3 for both planning and writing (selected option)
   thread = {"configurable": {"thread_id": str(uuid.uuid4()),
                              "search_api": os.getenv("SEARCH_API","gemini"),
                              "planner_provider": "openai",
                              "planner_model": os.getenv("DEEPRESEARCH_MODEL","o3-mini"),
                              "writer_provider": "openai",
                              "writer_model": os.getenv("DEEPRESEARCH_MODEL","o3-mini"),
                              "max_search_depth": 2,
                              "report_structure": REPORT_STRUCTURE,
                              "base_url": os.getenv("DEEPRESEARCH_ENDPOINT","https://api.deepresearch.ai/v1"),
                              "api_key": os.getenv("DEEPRESEARCH_API_KEY","gemini-api-key"),}
   }
   topic = task.format(topic=topic)
   async for event in graph.astream({"topic": topic}, thread, stream_mode="updates"):
      if '__interrupt__' in event:
         interrupt_value = event['__interrupt__'][0].value

   # Display the final generated report
   # Retrieve the completed report from the graph's state and format it for display
   
   final_state = graph.get_state(thread)
   report = final_state.values.get('completed_sections')
   print(len(report))
   # print(report[0].content)
   report_content = "\n\n".join(section["content"] for section in report)
   
   with open("output/deepresearch_report.md", "w", encoding="utf-8") as f:
      f.write(report_content)
   return report_content

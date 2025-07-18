from typing import Annotated, Optional
from langgraph.graph import MessagesState
from open_deep_research.state import Section, SearchQuery
import operator
from pydantic import BaseModel, Field

class ClarifyWithUser(BaseModel):
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )

class SectionOutput(BaseModel):
    section_content: str = Field(
        description="The content of the section.",
    )

class ReportStateInput(MessagesState):
    """InputState is only 'messages'"""
    already_clarified_topic: Optional[bool] = None # If the user has clarified the topic with the agent
    
class ReportStateOutput(MessagesState):
    final_report: str
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: str # String of formatted source content from web search

class ReportState(MessagesState):
    already_clarified_topic: Optional[bool] = None # If the user has clarified the topic with the agent
    feedback_on_report_plan: Annotated[list[str], operator.add] # List of feedback on the report plan
    sections: list[Section] # List of report sections 
    completed_sections: Annotated[list, operator.add] # Send() API key
    report_sections_from_research: str # String of any completed sections from research to write final sections
    final_report: str # Final report
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: Annotated[str, operator.add] # String of formatted source content from web search

class SectionState(MessagesState):
    section: Section # Report section  
    search_iterations: int # Number of search iterations done
    search_queries: list[SearchQuery] # List of search queries
    source_str: str # String of formatted source content from web search
    report_sections_from_research: str # String of any completed sections from research to write final sections
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API

class SectionOutputState(MessagesState):
    completed_sections: list[Section] # Final key we duplicate in outer state for Send() API
    # for evaluation purposes only
    # this is included only if configurable.include_source_str is True
    source_str: str # String of formatted source content from web search
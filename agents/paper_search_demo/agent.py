import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from typing import Any, Dict
import openai


os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = ""

from google.adk.agents import LlmAgent

# Configure SSE params
sse_params = SseServerParams(
    url="",  
)

toolset = MCPToolset(
    connection_params=SseServerParams(
        url="",
    ),
)

root_agent = Agent(
    name="mcp_sse_agent",
    model=LiteLlm(model="azure/gpt-4o"),
    instruction="You are an intelligent assistant capable of using external tools via MCP.",
    tools=[toolset]
)

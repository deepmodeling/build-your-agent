import asyncio
import os
from pathlib import Path
from typing import Any, Dict

import nest_asyncio
from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams, MCPToolset
from google.genai import types

load_dotenv()
nest_asyncio.apply()


# Global Configuration
BOHRIUM_EXECUTOR = {
    "type": "dispatcher",
    "machine": {
        "batch_type": "Bohrium",
        "context_type": "Bohrium",
        "remote_profile": {
            "email": os.getenv("BOHRIUM_EMAIL"),
            "password": os.getenv("BOHRIUM_PASSWORD"),
            "program_id": int(os.getenv("BOHRIUM_PROJECT_ID")),
            "input_data": {
                "image_name": "registry.dp.tech/dptech/dp/native/prod-19853/dpa-mcp:0.0.0",
                "job_type": "container",
                "platform": "ali",
                "scass_type": "1 * NVIDIA V100_32g"
            }
        }
    }
}
LOCAL_EXECUTOR = {
    "type": "local"
}
BOHRIUM_STORAGE = {
    "type": "bohrium",
    "username": os.getenv("BOHRIUM_EMAIL"),
    "password": os.getenv("BOHRIUM_PASSWORD"),
    "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
}


server_url = "http://kqti1328990.bohrium.tech:50001/sse"
session_service = InMemorySessionService()

# Initialize MCP tools and agent
mcp_tools = CalculationMCPToolset(
    connection_params=SseServerParams(url=server_url),
    storage=BOHRIUM_STORAGE,
    executor=BOHRIUM_EXECUTOR
)


root_agent = LlmAgent(
    model=LiteLlm(model="azure/gpt-4o"),
    name="dpa_calculations_agent",
    description="An agent specialized in computational research using Deep Potential",
    instruction=(
        "You are an expert in materials science and computational chemistry. "
        "Help users perform Deep Potential calculations including structure optimization, molecular dynamics and property calculations. "
        "Use default parameters if the users do not mention, but let users confirm them before submission. "
        "Always verify the input parameters to users and provide clear explanations of results."
    ),
    tools=[mcp_tools],
)
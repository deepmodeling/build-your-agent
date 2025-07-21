import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict

import nest_asyncio
from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk import Agent
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.genai import types

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()
nest_asyncio.apply()

# Global Configuration
BOHRIUM_EXECUTOR_CALC = {
    "type": "dispatcher",
    "machine": {
        "batch_type": "Bohrium",
        "context_type": "Bohrium",
        "remote_profile": {
            "email": os.getenv("BOHRIUM_EMAIL"),
            "password": os.getenv("BOHRIUM_PASSWORD"),
            "program_id": int(os.getenv("BOHRIUM_PROJECT_ID")),
            "input_data": {
                "image_name": "registry.dp.tech/dptech/dp/native/prod-19853/dpa-mcp:dev-0704",
                "job_type": "container",
                "platform": "ali",
                "scass_type": "1 * NVIDIA V100_32g"
            }
        }
    }
}
BOHRIUM_EXECUTOR_TE = {
    "type": "dispatcher",
    "machine": {
        "batch_type": "Bohrium",
        "context_type": "Bohrium",
        "remote_profile": {
            "email": os.getenv("BOHRIUM_EMAIL"),
            "password": os.getenv("BOHRIUM_PASSWORD"),
            "program_id": int(os.getenv("BOHRIUM_PROJECT_ID")),
            "input_data": {
                "image_name": "registry.dp.tech/dptech/dp/native/prod-435364/agents:0.1.0",
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

print('-----', BOHRIUM_STORAGE)


mcp_tools_dpa = CalculationMCPToolset(
    connection_params=SseServerParams(url="https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=d642e9e197f64539b3e0363d500a96f1"),
    # connection_params=SseServerParams(url="http://pfmx1355864.bohrium.tech:50002/sse"),
    storage=None,
    executor=None,
    executor_map={
        "build_structure": None
    }
)
mcp_tools_thermoelectric = CalculationMCPToolset(
    connection_params=SseServerParams(url="https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=1c1f2140a5504ebcb680f6a7fa2c03db"),
    storage=None,
    executor=BOHRIUM_EXECUTOR_TE
)
# mcp_tools_superconductor = CalculationMCPToolset(
#     connection_params=SseServerParams(url="https://superconductor-ambient-010-uuid1750845273.app-space.dplink.cc/sse?token=57578d394b564682943a723697f992b1"),
#     storage=BOHRIUM_STORAGE,
#     executor=None
# )
rootagent = LlmAgent(
    model=LiteLlm(model="deepseek/deepseek-chat"),
    name="dpa_agent",
    description="An agent specialized in computational research using Deep Potential",
    instruction=(
        "You are an expert in materials science and computational chemistry. "
        "Help users perform Deep Potential calculations including structure optimization, molecular dynamics and property calculations. "
        "Use default parameters if the users do not mention, but let users confirm them before submission. "
        "Always verify the input parameters to users and provide clear explanations of results."
    ),
    tools=[
        mcp_tools_dpa, 
        mcp_tools_thermoelectric, 
        # mcp_tools_superconductor
    ],
)

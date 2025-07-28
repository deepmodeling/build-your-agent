import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict

import nest_asyncio
from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()
nest_asyncio.apply()

AK = os.getenv("AK")
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
HTTPS_STORAGE = {
  "type": "https",
  "plugin": {
        "type": "bohrium",
        "username": os.getenv("BOHRIUM_EMAIL"),
        "password": os.getenv("BOHRIUM_PASSWORD"),
        "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
    }
}

print('-----', HTTPS_STORAGE)


mcp_tools_dpa = CalculationMCPToolset(
    connection_params=SseServerParams(url="https://dpa-uuid1750659890.app-space.dplink.cc/sse?token=a0d87a7abf8d47cb92403018fd4a9468"),
    # connection_params=SseServerParams(url="http://pfmx1355864.bohrium.tech:50002/sse"),
    storage=HTTPS_STORAGE,
    executor=None,
    executor_map={
        "build_structure": None
    }
)
mcp_tools_thermoelectric = CalculationMCPToolset(
    connection_params=SseServerParams(url="https://thermoelectricmcp000-uuid1750905361.app-space.dplink.cc/sse?token=1c1f2140a5504ebcb680f6a7fa2c03db"),
    storage=HTTPS_STORAGE,
    executor=BOHRIUM_EXECUTOR_TE
)
# mcp_tools_superconductor = CalculationMCPToolset(
#     connection_params=SseServerParams(url="https://superconductor-ambient-010-uuid1750845273.app-space.dplink.cc/sse?token=57578d394b564682943a723697f992b1"),
#     storage=HTTPS_STORAGE,
#     executor=None
# )
root_agent = LlmAgent(
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

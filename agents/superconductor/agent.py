import os
import nest_asyncio
from dotenv import load_dotenv
from dp.agent.adapter.adk import CalculationMCPToolset
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams

# Load credentials
nest_asyncio.apply()
load_dotenv()

# === Bohrium config ===
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
                "image_name": "registry.dp.tech/dptech/dp/native/prod-435364/dpa-superconductor-agent:0.1.0",
                "job_type": "container",
                "platform": "ali",
                "scass_type": "c12_m92_1 * NVIDIA V100"
            }
        }
    }
}

BOHRIUM_STORAGE = {
    "type": "bohrium",
    "username": os.getenv("BOHRIUM_EMAIL"),
    "password": os.getenv("BOHRIUM_PASSWORD"),
    "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
}

# === Server config ===
server_url = "http://teca1308705.bohrium.tech:50002/sse"
session_service = InMemorySessionService()

# === MCP toolset ===
mcp_tools = CalculationMCPToolset(
    connection_params=SseServerParams(url=server_url),
    storage=BOHRIUM_STORAGE,
    executor=BOHRIUM_EXECUTOR
)

# === Define agent ===
root_agent = LlmAgent(
    model=LiteLlm(model="azure/gpt-4o"),
    name="gpt_superconductor_agent",
    description="Helps with Deep Potential Model predict critical temperature for materials at ambient and high pressure",
    instruction="""
        Use MCP tools when structure input is provided. Otherwise, respond naturally to user queries.
        If users did not provide necessary parameters, ALWAYS use default but let users confirm before job submission.
    """,
    tools=[mcp_tools]
)


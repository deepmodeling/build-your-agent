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
from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams
from google.genai import types

load_dotenv()
nest_asyncio.apply()


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
                "image_name": "registry.dp.tech/dptech/dp/native/prod-19853/deepmd-kit-with-pmg:v3.1.0a",
                "job_type": "container",
                "platform": "ali",
                "scass_type": "1 * NVIDIA V100_32g"
            }
        }
    }
}
<<<<<<< HEAD
LOCAL_EXECUTOR = {
    "type": "local"
}
BOHRIUM_STORAGE = {
=======
BOHRIUM_STORAGE  = {
>>>>>>> main
    "type": "bohrium",
    "username": os.getenv("BOHRIUM_EMAIL"),
    "password": os.getenv("BOHRIUM_PASSWORD"),
    "project_id": int(os.getenv("BOHRIUM_PROJECT_ID"))
}


class DPACalculatorAgent:
    def __init__(self, server_url: str):
        self.agent = None
        self.runner = None
        self.session_service = InMemorySessionService()
        self.server_url = server_url
    async def initialize(self):
        """Initialize the agent with MCP tools"""
        # Configure MCP connection
        mcp_tools = await CalculationMCPToolset(
            connection_params=SseServerParams(
                url=self.server_url,  
            ),
<<<<<<< HEAD
            storage=BOHRIUM_STORAGE,    
        ).get_tools()
        print(f"✅ MCP tools initialized successfully. {[t.name for t in mcp_tools]}")
        for tool in mcp_tools:
            if tool.name == "build_structure":
                tool.executor = LOCAL_EXECUTOR
            else:
                tool.executor = BOHRIUM_EXECUTOR    
=======
            executor=BOHRIUM_EXECUTOR,  
            storage=BOHRIUM_STORAGE,    
        ).get_tools()
>>>>>>> main
        # Create the agent
        self.agent = LlmAgent(
            model=LiteLlm(model="azure/gpt-4o"),
            name="dpa_calculations_agent",
            description="An agent specialized in computational research using Deep Potential",
            instruction=(
                "You are an expert in materials science and computational chemistry. "
                "Help users perform Deep Potential calculations including structure optimization, molecular dynamics and property calculations. "
<<<<<<< HEAD
                "Use default parameters if the users do not mention, but let users confirm them before submission. "
                "Always verify the input parameters to users and provide clear explanations of results."
=======
                "Always verify detinput parameters to users and provide clear explanations of results."
>>>>>>> main
            ),
            tools=[*mcp_tools],
        )
        # Initialize runner
        self.runner = Runner(
            app_name="dpa_calculations",
            agent=self.agent,
            session_service=self.session_service,
        )
    async def run_dpa_calculators(self) -> Dict[str, Any]:
        """Run DPA calculations through the agent"""
        session = await self.session_service.create_session(
            state={},
            app_name="dpa_calculations",
            user_id="materials_researcher"
        )
        while True:
            user_input = input("🧑 User: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Task ended.")
                break
            content = types.Content(role="user", parts=[types.Part(text=user_input)])
            events_async = self.runner.run_async(
                session_id=session.id,
                user_id=session.user_id,
                new_message=content
            )
            try:
                async for event in events_async:
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                role = event.content.role
                                if role == "user":
                                    print(f"🧑 User: {part.text}")
                                elif role == "model":
                                    print(f"🤖 Agent: {part.text}")
            finally:
                await events_async.aclose() 
    def _extract_results(self, text: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "message": text,
            "data": {
                "raw_output": text
            }
        }

<<<<<<< HEAD
async def main():
    agent = DPACalculatorAgent(server_url="http://kqti1328990.bohrium.tech:50001/sse")
=======

async def main():
    agent = DPACalculatorAgent(server_url="http://<remote-machine-url>:50001/sse")
>>>>>>> main
    await agent.initialize()
    
    
    print("🚀 Starting calculations with DPA model...")
    try:
        results = await agent.run_dpa_calculators()
        print("📊 Results:", results)
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
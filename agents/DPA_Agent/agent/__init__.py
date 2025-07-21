"""
NexusAgent Symbolic Regression

A research-grade symbolic regression workflow orchestration system 
that automatically transforms raw data into scientifically interpretable mathematical models.
"""

from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=False)

__version__ = "1.0.0"
__author__ = "NexusAgent Team"
__license__ = "MIT"

# 从 subagent 导入 rootagent
from agent.agent import rootagent

__all__ = [
    "rootagent",
]

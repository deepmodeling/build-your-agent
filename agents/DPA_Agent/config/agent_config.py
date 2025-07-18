"""
Agent Configuration Loader

This module provides a centralized configuration system for different agent implementations.
To switch between different agents, modify the agent-config.json file.
"""

import json
from pathlib import Path
from typing import Dict, Any
import importlib

class AgentConfig:
    def __init__(self, config_path: str = "config/agent-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            # Fallback to default config if file doesn't exist
            return self._get_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration for NexusAgent SR"""
        return {
            "agent": {
                "name": "DPA Calculators",
                "description": "",
                "welcomeMessage": "Start your simulation by starting a conversation.",
                "module": "DPA_subagent.subagent",
                "rootAgent": "rootagent"
            },
            "ui": {
                "title": "DPA Calculators",
                "features": {
                    "showFileExplorer": True,
                    "showSessionList": True
                }
            },
            "files": {
                "outputDirectory": "output",
                "watchDirectories": ["output"]
            },
            "websocket": {
                "host": "localhost",
                "port": 8000
            }
        }
    
    def get_agent(self):
        """Dynamically import and return the configured agent"""
        agent_config = self.config.get("agent", {})
        module_name = agent_config.get("module", "DPA_subagent.subagent")
        agent_name = agent_config.get("rootAgent", "rootagent")
        
        try:
            module = importlib.import_module(module_name)
            return getattr(module, agent_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load agent {agent_name} from {module_name}: {e}")
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI-specific configuration"""
        return self.config.get("ui", {})
    
    def get_files_config(self) -> Dict[str, Any]:
        """Get file handling configuration"""
        return self.config.get("files", {})
    
    def get_websocket_config(self) -> Dict[str, Any]:
        """Get WebSocket configuration"""
        return self.config.get("websocket", {})
    
    def get_tool_display_name(self, tool_name: str) -> str:
        """Get display name for a tool"""
        tools_config = self.config.get("tools", {})
        display_names = tools_config.get("displayNames", {})
        return display_names.get(tool_name, tool_name)
    
    def is_long_running_tool(self, tool_name: str) -> bool:
        """Check if a tool is marked as long-running"""
        tools_config = self.config.get("tools", {})
        long_running = tools_config.get("longRunningTools", [])
        return tool_name in long_running

# Singleton instance
agent_config = AgentConfig()
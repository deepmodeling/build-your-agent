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
        """Provide default configuration for Agent"""
        return {
            "agent": {
                "name": "My Agent",
                "description": "智能符号回归分析系统",
                "welcomeMessage": "输入您的数据文件路径，开始符号回归分析",
                "module": "agent.subagent",
                "rootAgent": "rootagent"
            },
            "ui": {
                "title": "Agent",
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
        agentconfig = self.config.get("agent", {})
        module_name = agentconfig.get("module", "agent.subagent")
        agentname = agentconfig.get("rootAgent", "rootagent")
        
        try:
            module = importlib.import_module(module_name)
            return getattr(module, agentname)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load agent {agentname} from {module_name}: {e}")
    
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
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration including port and allowed hosts"""
        # 默认主机始终被允许
        default_hosts = ["localhost", "127.0.0.1", "0.0.0.0"]
        
        server_config = self.config.get("server", {})
        
        # 合并默认主机和用户定义的额外主机
        user_hosts = server_config.get("allowedHosts", [])
        all_hosts = list(set(default_hosts + user_hosts))  # 使用 set 去重
        
        return {
            "port": server_config.get("port", 50002),
            "allowedHosts": all_hosts
        }

# Singleton instance
agentconfig = AgentConfig()
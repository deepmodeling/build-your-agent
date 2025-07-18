# Agent Configuration Guide

## Overview

The NexusAgent UI system is designed to be agent-agnostic. You can easily switch between different agent implementations by modifying the configuration file.

## Configuration File

The main configuration file is located at `config/agent-config.json`.

## Switching Agents

To use a different agent with the UI, follow these steps:

### 1. Update the Agent Configuration

Edit `config/agent-config.json`:

```json
{
  "agent": {
    "name": "Your Agent Name",
    "description": "Your agent description",
    "welcomeMessage": "Welcome message for users",
    "module": "your_module.submodule",  // Python module path
    "rootAgent": "your_agent_instance"   // Agent instance name
  }
}
```

### 2. Example Configurations

#### NexusAgent SR (Default)
```json
{
  "agent": {
    "name": "NexusAgent SR",
    "description": "智能符号回归分析系统",
    "welcomeMessage": "输入您的数据文件路径，开始符号回归分析",
    "module": "DPA_subagent.subagent",
    "rootAgent": "rootagent"
  }
}
```

#### Custom Research Agent
```json
{
  "agent": {
    "name": "Research Assistant",
    "description": "AI-powered research system",
    "welcomeMessage": "What would you like to research today?",
    "module": "research_agent.main",
    "rootAgent": "research_agent"
  }
}
```

### 3. UI Customization

Customize the UI appearance and features:

```json
{
  "ui": {
    "title": "Your App Title",
    "theme": {
      "primaryColor": "blue",
      "secondaryColor": "purple"
    },
    "features": {
      "showFileExplorer": true,    // Show/hide file explorer
      "showSessionList": true,      // Show/hide session management
      "enableFileUpload": false     // Enable file upload feature
    }
  }
}
```

### 4. File Management

Configure which directories to watch and display:

```json
{
  "files": {
    "outputDirectory": "output",        // Default output directory
    "watchDirectories": ["output", "results"],  // Directories to display
    "fileExtensions": {
      "supported": ["json", "md", "txt", "csv", "py"],
      "defaultViewer": {
        "json": "code",
        "md": "markdown",
        "csv": "table"
      }
    }
  }
}
```

### 5. Tool Display Names

Customize how tools are displayed in the UI:

```json
{
  "tools": {
    "displayNames": {
      "your_tool_name": "User-Friendly Name",
      "another_tool": "Another Display Name"
    },
    "longRunningTools": [
      "heavy_computation_tool",
      "data_processing_tool"
    ]
  }
}
```

## Implementation Requirements

For your agent to work with this UI system, it must:

1. **Be compatible with Google ADK**: The agent should work with Google's Agent Development Kit
2. **Use standard message format**: Messages should follow the format used by the WebSocket server
3. **Implement required methods**: Your agent should handle user messages and return appropriate responses

## Quick Start

1. Install your agent module:
   ```bash
   pip install your-agent-package
   ```

2. Update `config/agent-config.json` with your agent details

3. Restart the server:
   ```bash
   ./start-nexus.sh
   ```

4. The UI will automatically load your agent configuration

## Environment Variables

You can also use environment variables to override configuration:

```bash
export AGENT_MODULE=my_agent.main
export AGENT_NAME=my_agent
export UI_TITLE="My Custom Agent"
```

## Troubleshooting

- **Agent not loading**: Check that the module path and agent name are correct
- **UI not updating**: Clear browser cache and reload
- **WebSocket errors**: Ensure your agent is compatible with the message format

## Example: Creating a Compatible Agent

```python
from google.adk import Agent
from google.adk.models import LiteLlm

# Your agent implementation
my_agent = Agent(
    name="MyAgent",
    model=LiteLlm(model="gpt-4"),
    description="My custom agent",
    tools=[...],
    instruction="..."
)

# Export as the root agent
rootagent = my_agent
```
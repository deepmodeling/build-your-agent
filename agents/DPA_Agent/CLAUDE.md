# CLAUDE.md
用中文回答我
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Agent system built with Google ADK (Agent Development Kit) that provides a WebSocket-based chat interface with a React frontend. The system is designed to be extensible for building custom AI agents.

## Commands

### Starting the System
```bash
# Start both backend and frontend
./start-agent.sh

# Or manually:
# Backend (WebSocket server on port 8000)
python websocket-server.py

# Frontend (React app on port 5173)
cd ui && npm run dev
```

### Frontend Development
```bash
cd ui
npm install         # Install dependencies
npm run dev         # Start development server
npm run build       # Build for production
npm run type-check  # Run TypeScript type checking
```

### Python Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# The project uses Google ADK - no specific test runner configured
```

## Architecture

### Core Components

1. **WebSocket Server** (`websocket-server.py`):
   - FastAPI-based server providing WebSocket connections
   - Manages sessions and agent interactions
   - Uses Google ADK's Runner and InMemorySessionService
   - Handles multiple concurrent client connections

2. **Agent Configuration** (`config/agent_config.py`):
   - Dynamic agent loading system
   - Configurable via `config/agent-config.json`
   - Default configuration points to `agent.agent.root_agent`

3. **Frontend** (`ui/`):
   - React + TypeScript + Vite
   - WebSocket client for real-time communication
   - Session management with persistent UI state
   - File explorer for output directory

4. **Agent Implementation** (`agent/agent.py`):
   - Uses Google ADK Agent framework
   - Configurable with LiteLLM for model selection
   - Currently configured for DeepSeek or Azure OpenAI GPT-4

### Key Design Patterns

1. **Session Management**: Each WebSocket connection maintains its own session context with isolated Runner and SessionService instances.

2. **Message Protocol**: JSON-based WebSocket messages with types: 'user', 'assistant', 'tool', 'system', 'error', 'complete'

3. **Tool Execution**: Agent tools are executed asynchronously with status updates sent via WebSocket

4. **File Watching**: Output directory is monitored and file changes are broadcast to connected clients

## Environment Configuration

Create `agent/.env` file with:
```bash
# For DeepSeek
MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=your_key_here

# For Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

# Optional search tools
TAVILY_API_KEY=your_key
```

## Important Implementation Details

1. **Agent Module Loading**: The system dynamically imports agents based on `agent-config.json`. The default expects `root_agent` from module `agent`.

2. **WebSocket Connection Lifecycle**: Each connection gets a unique user_id and maintains independent state. Disconnections are handled gracefully.

3. **Error Handling**: Tool execution errors and agent failures are caught and sent as error messages to the client.

4. **File Output**: Results are typically written to the `output/` directory which is watched by the file explorer component.

## Common Development Tasks

### Adding a New Agent
1. Create your agent module in `agent/`
2. Update `config/agent-config.json` to point to your agent
3. Ensure your agent exports the expected variable name (default: `root_agent`)

### Extending the UI
See `docs/UI_EXTENSION_GUIDE.md` for detailed instructions on:
- Adding new components
- Extending message types
- Creating new pages
- Custom WebSocket handlers

### Modifying WebSocket Protocol
1. Update message handlers in `websocket-server.py`
2. Add corresponding TypeScript types in frontend
3. Update `ChatInterface.tsx` to handle new message types
# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NexusAgent-SR is an intelligent agent system for Symbolic Regression built on Google's ADK (Agent Development Kit). It automatically converts raw data into interpretable mathematical models using multi-agent collaboration and AI-driven research capabilities.

## Key Commands

### Setup and Installation
```bash
# Backend setup
cd DPA_subagent
pip install -r requirements.txt

# Frontend setup
cd nexus-ui
npm install
```

### Running the System
```bash
# Option 1: Use the startup script (recommended)
./start-nexus.sh

# Option 2: Run components separately
# Terminal 1 - Backend WebSocket server
python nexus-websocket-server.py

# Terminal 2 - Frontend development server
cd nexus-ui
npm run dev

# Option 3: Via Google ADK Web Interface (legacy)
adk web

# Direct symbolic regression (no UI)
python run_sr.py

# Deep research module
python research.py
```

### Development Commands
- **Run notebooks**: Use `jupyter notebook` to run test.ipynb files
- **Check agent status**: View task status in `output/task_status.json`
- **View results**: Check `output/summarize_report.md` and `output/results.json`

## Architecture Overview

### System Components
The system now includes a modern web UI in addition to the agent framework:

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (React)                        │
│                  localhost:5173                          │
└────────────────────────┬────────────────────────────────┘
                         │ WebSocket
┌────────────────────────┴────────────────────────────────┐
│              WebSocket Server (FastAPI)                  │
│                  localhost:8000                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                   Google ADK Agents                      │
│                                                          │
│  NexusAgent (root) - Main orchestrator in subagent.py   │
│  ├── ResearchAgent - Data analysis                      │
│  └── SRIterationAgent - Symbolic regression workflow    │
│      ├── PriorAgent - Configures operators              │
│      ├── SymbolicAgent - Executes regression            │
│      └── SummarizeAgent - Generates reports             │
└──────────────────────────────────────────────────────────┘
```

### Core Modules

1. **UI Layer**:
   - **nexus-ui/**: React-based frontend application
     - `src/components/ChatInterface.tsx`: Main chat interface with WebSocket connection
     - `src/styles/`: TailwindCSS styling
   - **nexus-websocket-server.py**: FastAPI WebSocket server
     - Handles real-time communication between UI and agents
     - Manages session state and message routing

2. **Agent Layer**:
   - **DPA_subagent/subagent.py**: New agent implementation using Google ADK
     - Defines agent hierarchy and communication
     - Manages asynchronous task execution
     - Coordinates multi-round iterations
   - **DPA_subagent/agent.py**: (Deprecated) Original agent orchestration

2. **DPA_subagent/tool/**: Tool implementations
   - `pysr.py`: Standard symbolic regression using PySR library
   - `deepresearch.py`: AI-powered literature research and knowledge extraction
   - `summarize_report.py`: Automatic scientific report generation
   - `iteration_manager.py`: Manages iteration history for multi-round experiments
   - `task_manager.py`: Async task tracking and status management

3. **DPA_subagent/prompt/**: Agent prompts and templates
   - Contains structured prompts for each agent role
   - Defines output formats and research guidelines

### Key Design Patterns

1. **Asynchronous Task Management**: Long-running tasks (like symbolic regression) are executed asynchronously with status tracking via `task_manager.py`

2. **Iteration Memory**: The system maintains iteration history to improve results across multiple rounds using `iteration_manager.py`

3. **Tool Registration**: All tools are registered in `agent_tool.py` and made available to agents through the ADK framework

4. **Structured Outputs**: Each agent produces structured JSON outputs that are consumed by downstream agents

## Environment Configuration

Required `.env` file in project root:
```
MODEL=gpt-4o-mini
DEEPRESEARCH_MODEL=gpt-4o-mini
DEEPRESEARCH_ENDPOINT=https://api.openai.com/v1
DEEPRESEARCH_GEMINI_API_KEY=your_gemini_api_key
SEARCH_API=your_search_api_key
```

## Working with the Codebase

### Adding New Features
- New symbolic regression algorithms: Extend classes in `tool/pysr*.py`
- New agent capabilities: Add to agent hierarchy in `subagent.py`
- New tools: Implement in `tool/` and register in `agent_tool.py`
- UI components: Add React components in `nexus-ui/src/components/`
- WebSocket messages: Extend message handling in `nexus-websocket-server.py`
- For detailed UI extension guide, see `docs/UI_EXTENSION_GUIDE.md`

### Data Flow

#### With UI:
1. User interacts with React frontend at localhost:5173
2. Frontend sends messages via WebSocket to backend (localhost:8000)
3. Backend routes messages to appropriate agents via Google ADK
4. Agents process requests and send updates back through WebSocket
5. Frontend displays real-time updates, tool execution status, and results
6. User can browse and view output files directly in the UI

#### Without UI (Direct):
1. User provides data file path and task description
2. ResearchAgent analyzes data and generates feature descriptions
3. PriorAgent configures symbolic regression parameters based on analysis
4. SymbolicAgent executes regression (async) and monitors progress
5. SummarizeAgent generates comprehensive scientific report
6. Results saved to `output/` directory

### Important Files and Locations
- **Input data**: Typically in `data/` directory (CSV format)
- **Task configuration**: Auto-generated in `output/task_config_pysr.json`
- **Results**: 
  - `output/summarize_report.md` - Final scientific report
  - `output/results.json` - Complete regression results
  - `output/best.txt` - Best discovered expression
- **Task status**: `output/task_status.json` for async task tracking

### Error Handling
- The system uses try-except blocks extensively for robustness
- Failed tasks are logged with error details in task status
- Agents can retry operations based on error feedback

## Testing Approach
While no formal test suite exists, the project includes example notebooks:
- `test.ipynb` - Basic functionality tests
- `open_deep_research/test.ipynb` - Research module tests
- `open_deep_research/multi_agent.ipynb` - Multi-agent workflow examples

Run these notebooks to verify system functionality after changes.

### UI Testing
- Frontend: Run `npm run dev` in `nexus-ui/` and test in browser
- WebSocket: Monitor connections in browser DevTools Network tab
- Backend: Check logs in terminal running `nexus-websocket-server.py`

## Troubleshooting

### Common Issues
1. **UI not connecting**: Ensure backend is running on port 8000
2. **Blank output files**: Check `output/task_status.json` for errors
3. **Agent timeout**: Verify API keys in `.env` file
4. **Frontend build errors**: Run `npm install` to update dependencies
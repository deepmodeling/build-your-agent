Here's a comprehensive README.md for your project:

```markdown
# Deep Potential Agent (DPA) for Materials Science Calculations

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A powerful agent system for performing materials science calculations using Deep Potential (DP) models, with integration to Bohrium computing platform.

## Features

- **Structure Building**: Create bulk, surface, and interface structures
- **Structure Optimization**: Optimize crystal structures using DP models
- **Phonon Calculations**: Compute phonon spectra and thermal properties
- **Interactive Agent**: Natural language interface for computational workflows
- **Cloud Integration**: Seamless execution on Bohrium computing platform

## Components

### `agent.py`
The interactive agent that provides a natural language interface for materials calculations.

Key functionalities:
- Initializes with Deep Potential calculation tools
- Manages user sessions and workflows
- Processes natural language instructions
- Coordinates calculation execution

### `mcp_server.py`
The server that provides computational tools via MCP (Materials Calculation Protocol).

Available tools:
- `build_structure`: Construct crystal structures (bulk, surface, interface)
- `optimize_crystal_structure`: Geometry optimization with DP models
- `calculate_phonon`: Phonon spectrum and thermal property calculations

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/dpa-agent.git
   cd dpa-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your Bohrium credentials:
   ```
   BOHRIUM_EMAIL=your@email.com
   BOHRIUM_PASSWORD=your_password
   BOHRIUM_PROJECT_ID=your_project_id
   ```

## Usage

### Running the MCP Server

Start the calculation server:
```bash
python mcp_server.py
```
W
The server provides these endpoints:
- `http://localhost:50001/sse` - SSE endpoint for agent communication
- Tool-specific endpoints for direct API access


### Running the Agent

Start the interactive agent:
```bash
python agent.py
```

## Best Practices
### 1. Build structures using ASE

```
🚀 Starting calculations with DPA model...
🧑 User: Build a bulk crystal structure for Gold (Au) with an FCC crystal structure and a lattice constant a of 4.08 Å; Then optimize this structure and calculate the phonon spectra with the optimized structures. Use default parameters if I did not mention, but 
let me confirm them before submission.
🤖 Agent: Let's go through the parameters for building the bulk crystal structure and then I'll outline the steps for optimization and phonon calculation:

### Building the Bulk Crystal Structure:
- **Material**: Gold (Au)
- **Crystal Structure**: FCC (Face-Centered Cubic)
- **Lattice Constant a**: 4.08 Å
- **Conventional**: True (using the conventional standard cell)
- **Output File**: default is 'structure.cif'

### Structure Optimization:
- **Model Path**: Default (DPA-2.4-7M)
- **Force Tolerance**: 0.01 eV/Å (default)
- **Max Iterations**: 100 steps (default)

### Phonon Calculation:
- **Supercell Matrix**: Default [3,3,3]
- **Displacement Distance**: 0.005 Å (default)
- **Plot Path**: 'phonon_band.png' (default)

Please confirm these parameters, and once you agree, I will proceed with the calculations.
🧑 User: Continue.
```

Then the agent will execute the calculations and provide the results.





## License

MIT License - See [LICENSE](LICENSE) for details.

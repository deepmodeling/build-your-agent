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
🤖 Agent: Let's proceed step by step:

1. **Build the Bulk Crystal Structure**:
   - Material: Gold (Au)
   - Crystal Structure: FCC
   - Lattice Constant \(a\): 4.08 Å

2. **Optimize the Structure**:
   - Input Structure File: Will be based on the generated structure for Gold
   - Model Path: Default to "bohrium://13756/27666/store/upload/d7af9d6c-ae70-40b5-a85b-1a62269946b8/dpa-2.4-7M.pt"
   - Force Tolerance: Default 0.01 eV/Å
   - Maximum Iterations: Default 100 steps

3. **Calculate Phonon Spectra**:
   - CIF File: Will use the optimized structure from the previous step
   - Model Path: Default to "bohrium://13756/27666/store/upload/d7af9d6c-ae70-40b5-a85b-1a62269946b8/dpa-2.4-7M.pt"
   - Supercell Matrix: Default [3,3,3]
   - Displacement Distance: Default 0.005 Å
   - Plot Path: Default "phonon_band.png"

Please verify if all these parameters are acceptable or if you'd like to adjust any before I proceed.
🧑 User: yes
```

Then the agent will execute the calculations and provide the results.
```
🤖 Agent: Here's the completed workflow for the Gold (Au) FCC structure:

### 1. Built Crystal Structure
   - **Structure File**: [Structure CIF File](bohrium://13756/27666/store/26c43b894b97d2772ba3f079b969f6ada6b527fd/outputs/structure_file/structure.cif)

### 2. Optimization of Structure
   - **Optimized Structure**: [Optimized CIF File](bohrium://13756/27666/store/a63618b9e0ac1c814a7dc63966c7a22d9007aa65/outputs/optimized_structure/structure_optimized.cif)
   - **Optimization Trajectory**: [Trajectory File](bohrium://13756/27666/store/a63618b9e0ac1c814a7dc63966c7a22d9007aa65/outputs/optimization_traj/structure_optimization_traj.extxyz)
   - **Final Energy**: \(-12.67\) eV
   - **Message**: Successfully completed in 0 steps

### 3. Phonon Spectra Calculation
   - **Phonon Entropy**: 197.89 J/mol·K
   - **Helmholtz Free Energy**: \(-28.94\) kJ/mol
   - **Heat Capacity at Constant Volume**: 98.13 J/mol·K
   - **Maximum Phonon Frequency**: 4.47 THz (214.52 K)
   - **Band Structure Plot**: [Phonon Band Plot](bohrium://13756/27666/store/199687e0ec4c0809b2cd32716bf56be123e64e36/outputs/band_plot/phonon_band.png)
   - **Band Data (YAML)**: [Band YAML](bohrium://13756/27666/store/199687e0ec4c0809b2cd32716bf56be123e64e36/outputs/band_yaml/phonon_band_band.yaml)
   - **Band Data (DAT)**: [Band DAT File](bohrium://199687e0ec4c0809b2cd32716bf56be123e64e36/outputs/band_dat)

If you have any questions or need further assistance, feel free to ask!
```

If you want to change the parameters, you can prompt the user to change them. For example:
```
🧑 User: I want the Force Tolerance to be 0.05
```




## License

MIT License - See [LICENSE](LICENSE) for details.

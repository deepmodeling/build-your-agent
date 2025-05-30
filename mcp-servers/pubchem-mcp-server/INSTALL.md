# Installation Guide for PubChem MCP Server

This guide will help you set up and run the PubChem MCP Server on your system.

## Prerequisites

- Python 3.8 or newer
- pip (Python package manager)
- [Optional] RDKit for enhanced 3D structure handling

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/pubchem-mcp-server.git
cd pubchem-mcp-server
```

### 2. Install Dependencies

#### Basic Installation
```bash
cd python_version
pip install -e .
```

#### With RDKit Support (Recommended for Chemistry Applications)
```bash
# Install RDKit first (optional but recommended)
conda install -c conda-forge rdkit  # If using Conda environment

# Then install the server with RDKit support
pip install -e ".[rdkit]"
```

### 3. Run the Server

#### Using the Convenience Script
```bash
# From the repository root directory
./run_server.sh
```

#### Or Manually
```bash
cd python_version
python mcp_server.py
```

## Integration with Claude or Other MCP-capable Models

1. Locate your MCP settings file:
   - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
   - Claude Dev: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` (macOS)

2. Update the MCP settings file with the PubChem server configuration:
   ```json
   {
     "mcpServers": {
       "pubchem": {
         "command": "python3",
         "args": [
           "/full/path/to/pubchem-mcp-server/python_version/mcp_server.py"
         ],
         "env": {
           "PYTHONUNBUFFERED": "1"
         },
         "disabled": false,
         "autoApprove": [
           "get_pubchem_data",
           "download_structure"
         ]
       }
     }
   }
   ```

3. Replace `/full/path/to/` with the actual path to your repository.

4. Restart Claude or the MCP client application to load the new server.

## Verifying the Installation

Once the server is registered, you can test it with Claude by asking it to use the PubChem tools:

```
Can you tell me about the chemical properties of caffeine using the PubChem database?

Or

Can you retrieve the 3D structure of aspirin in XYZ format?
```

## Troubleshooting

- If the server fails to start, check the log file in `~/.pubchem-mcp/pubchem_mcp_server_*.log`
- Ensure Python 3.8+ is in your PATH
- Make sure the server script has executable permissions: `chmod +x run_server.sh`

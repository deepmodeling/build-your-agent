# PubChem MCP Server

A Model Context Protocol (MCP) server for retrieving chemical compound data from PubChem database(https://github.com/PhelanShao/pubchem-mcp-server).

## Overview

The first step in computational chemistry is usually modeling. Of course, if the chemical structure of a compound is already known, downloading it from PubChem is far better than having a language model generate a molecular coordinate out of thin air. PubChem MCP Server is a Python implementation of an MCP server that allows AI models to query chemical compound information from the PubChem database. It provides easy access to compound properties, 2D structures, and 3D molecular coordinates through a standard MCP interface.

## Features

- Query compounds by name or PubChem CID
- Retrieve comprehensive compound data including:
  - IUPAC name
  - Molecular formula
  - Molecular weight
  - SMILES notation
  - InChI and InChIKey
- Support for multiple output formats:
  - JSON (default)
  - CSV
  - XYZ (3D structure)
- Built-in caching system to improve performance
- Automatic retry mechanism for API reliability
- Fallback 3D structure generation if PubChem 3D is unavailable

## Requirements

- Python 3.8+
- Requests library
- RDKit (optional, for enhanced 3D structure handling)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/PhelanShao/pubchem-mcp-server.git
cd pubchem-mcp-server/python_version

# Install the package
pip install -e .

# For enhanced 3D structure handling, install with RDKit
pip install -e ".[rdkit]"
```

## MCP Configuration

To use the server with Claude or other MCP-capable AI models, add the following to your MCP configuration file:

```json
{
  "mcpServers": {
    "pubchem": {
      "command": "python3",
      "args": ["/path/to/pubchem-mcp-server/python_version/mcp_server.py"],
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

## Available Tools

### get_pubchem_data

Retrieves chemical compound structure and property data.

Parameters:
- `query` (required): Compound name or PubChem CID
- `format` (optional): Output format - "JSON" (default), "CSV", or "XYZ"
- `include_3d` (optional): Whether to include 3D structure (only valid when format is "XYZ")

Example use:
```
<use_mcp_tool>
<server_name>pubchem</server_name>
<tool_name>get_pubchem_data</tool_name>
<arguments>
{
  "query": "aspirin",
  "format": "JSON"
}
</arguments>
</use_mcp_tool>
```

### download_structure

Downloads structure files for a compound.

Parameters:
- `cid` (required): PubChem CID
- `format` (optional): File format - "sdf" (default), "mol", or "smi"
- `filename` (optional): Custom filename for the downloaded structure

Example use:
```
<use_mcp_tool>
<server_name>pubchem</server_name>
<tool_name>download_structure</tool_name>
<arguments>
{
  "cid": "2244",
  "format": "sdf"
}
</arguments>
</use_mcp_tool>
```

## Project Structure

```
pubchem-mcp-server/
├── python_version/               # Python implementation
│   ├── mcp_server.py             # Main MCP server script
│   ├── setup.py                  # Package installation script
│   ├── pubchem_mcp_server/       # Core package
│   │   ├── __init__.py
│   │   ├── pubchem_api.py        # PubChem API interaction
│   │   ├── xyz_utils.py          # 3D structure and XYZ format utilities
│   │   ├── server.py             # MCP server implementation
│   │   ├── cli.py                # Command-line interface
│   │   └── async_processor.py    # Asynchronous request handling
└── LICENSE
```

## Caching

The server uses a caching mechanism to improve performance:
- API responses are cached in memory
- 3D structure data is cached in `~/.pubchem-mcp/cache/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

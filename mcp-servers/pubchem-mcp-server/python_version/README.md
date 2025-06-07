# PubChem MCP Server - Python Implementation

This directory contains the Python implementation of the PubChem MCP Server.

## Directory Structure

- `mcp_server.py`: The main server script that can be directly executed
- `setup.py`: Package installation script
- `pubchem_mcp_server/`: Core package with modular implementation:
  - `__init__.py`: Package definition and version
  - `pubchem_api.py`: Core PubChem API interaction functions
  - `xyz_utils.py`: 3D structure handling and XYZ format utilities
  - `server.py`: MCP protocol server implementation
  - `cli.py`: Command-line interface
  - `async_processor.py`: Asynchronous request handling

## Installation

### Development Install

```bash
# From this directory
pip install -e .

# With RDKit support (optional but recommended for better 3D structure handling)
pip install -e ".[rdkit]"
```

## Running the Server

### As a standalone MCP server

```bash
# Directly run the server script
python mcp_server.py

# Or use the installed entry point
pubchem-mcp-server
```

### As a command-line tool

If you don't need the MCP server functionality, you can use the CLI:

```bash
# Query compound data
pubchem-mcp query aspirin

# Get 3D structure in XYZ format
pubchem-mcp query aspirin --format XYZ --include-3d

# Download structure file
pubchem-mcp download 2244 --format sdf --output aspirin.sdf
```

## Configuration

The server is configured to cache API responses to improve performance:
- In-memory cache for property data
- File-based cache for 3D structures in `~/.pubchem-mcp/cache/`

## Dependencies

- Required: Python 3.8+, requests
- Optional: RDKit (for enhanced 3D structure generation)

If RDKit is not available, the server will fall back to using a simplified SDF parser for XYZ format conversion.

#!/usr/bin/env python3
"""
PubChem MCP Server

A PubChem data query server compatible with the MCP protocol.
"""

import json
import sys
import os
import logging
import traceback
import requests
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure no buffering
os.environ['PYTHONUNBUFFERED'] = '1'

# Set up logging
log_dir = os.path.expanduser("~/.pubchem-mcp")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"pubchem_mcp_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("pubchem_mcp_server")

# Global cache
_cache: Dict[str, Dict[str, str]] = {}

# Create HTTP session
def create_session() -> requests.Session:
    """Create a requests session with retry functionality"""
    session = requests.Session()
    retry_strategy = requests.adapters.Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# PubChem API functions
def get_pubchem_data(query: str, format: str = 'JSON', include_3d: bool = False) -> str:
    """Get PubChem compound data"""
    logger.info(f"Getting PubChem data: query={query}, format={format}, include_3d={include_3d}")
    
    if not query or not query.strip():
        return "Error: Query cannot be empty"
    
    query_str = query.strip()
    is_cid = re.match(r'^\d+$', query_str) is not None
    cache_key = f"cid:{query_str}" if is_cid else f"name:{query_str.lower()}"
    identifier_path = f"cid/{query_str}" if is_cid else f"name/{query_str}"
    cid = query_str if is_cid else None
    
    # Check cache
    if cache_key in _cache:
        logger.info(f"Retrieving data from cache: {cache_key}")
        data = _cache[cache_key]
        if not cid:
            cid = data.get('CID')
            if not cid:
                return "Error: CID not found in cached data"
    else:
        # Define properties to retrieve
        properties = [
            'IUPACName',
            'MolecularFormula',
            'MolecularWeight',
            'CanonicalSMILES',
            'InChI',
            'InChIKey'
        ]
        
        # Build API URL
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{identifier_path}/property/{','.join(properties)}/JSON"
        
        try:
            session = create_session()
            response = session.get(url, timeout=180)
            response.raise_for_status()
            result = response.json()
            props = result.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            if not props:
                return "Error: Compound not found or no data available"
            
            if not cid:
                cid = str(props.get('CID'))
                if not cid:
                    return "Error: CID not found in response"
            
            # Create data dictionary
            data = {
                'IUPACName': props.get('IUPACName', ''),
                'MolecularFormula': props.get('MolecularFormula', ''),
                'MolecularWeight': str(props.get('MolecularWeight', '')),
                'CanonicalSMILES': props.get('CanonicalSMILES', ''),
                'InChI': props.get('InChI', ''),
                'InChIKey': props.get('InChIKey', ''),
                'CID': cid
            }
            
            # Update cache
            _cache[cache_key] = data
            if cid and f"cid:{cid}" != cache_key:
                _cache[f"cid:{cid}"] = data
                
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            try:
                if hasattr(e, 'response') and e.response:
                    error_data = e.response.json()
                    error_msg = error_data.get('Fault', {}).get('Details', [{}])[0].get('Message', str(e))
            except:
                pass
            return f"Error: {error_msg}"
    
    # Handle different output formats
    fmt = format.upper()
    
    # XYZ format - 3D structure
    if fmt == 'XYZ':
        if include_3d:
            try:
                # Get compound info
                compound_info = {
                    'id': data['CID'],
                    'name': data['IUPACName'],
                    'formula': data['MolecularFormula'],
                    'smiles': data['CanonicalSMILES'],
                    'inchikey': data['InChIKey']
                }
                
                # Get XYZ structure
                xyz_structure = get_xyz_structure(data['CID'], compound_info)
                
                if xyz_structure:
                    return xyz_structure
                else:
                    return "Error: Unable to generate 3D structure"
            except Exception as e:
                return f"Error: Error generating 3D structure: {str(e)}"
        else:
            return "Error: include_3d parameter must be true when using XYZ format"
    
    # CSV format
    elif fmt == 'CSV':
        headers = ['CID', 'IUPACName', 'MolecularFormula', 'MolecularWeight', 
                  'CanonicalSMILES', 'InChI', 'InChIKey']
        values = [data.get(h, '') for h in headers]
        return f"{','.join(headers)}\n{','.join(values)}"
    
    # Default JSON format
    else:
        return json.dumps(data, indent=2)

def get_xyz_structure(cid: str, compound_info: Dict[str, str]) -> Optional[str]:
    """Get XYZ format 3D structure for a compound"""
    try:
        # Get 3D structure from PubChem
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d&response_type=save"
        
        session = create_session()
        response = session.get(url)
        
        if response.status_code == 200 and response.text and "NO_3D_SCREENING_AVAILABLE" not in response.text:
            sdf_data = response.text
            xyz_data = convert_sdf_to_xyz(sdf_data, compound_info)
            if xyz_data:
                return xyz_data
    except Exception as e:
        logger.error(f"Error getting XYZ structure: {str(e)}")
    
    # Return error if fetching from PubChem fails
    return None

def convert_sdf_to_xyz(sdf_data: str, compound_info: Dict[str, str]) -> Optional[str]:
    """Convert SDF format to XYZ format"""
    try:
        # Parse SDF data
        lines = sdf_data.strip().split('\n')
        
        # Get atom count (usually in line 4)
        counts_line = lines[3].strip()
        atom_count = int(counts_line.split()[0])
        
        # Parse atom coordinates (starting from line 5)
        atoms = []
        for i in range(4, 4 + atom_count):
            if i < len(lines):
                parts = lines[i].strip().split()
                if len(parts) >= 4:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    element = parts[3]
                    atoms.append((element, x, y, z))
        
        # Create XYZ format
        xyz_lines = []
        xyz_lines.append(str(len(atoms)))
        xyz_lines.append(f"PubChem CID: {compound_info['id']} - {compound_info['name']} - Formula: {compound_info['formula']}")
        
        for element, x, y, z in atoms:
            xyz_lines.append(f"{element} {x:.6f} {y:.6f} {z:.6f}")
            
        return "\n".join(xyz_lines)
        
    except Exception as e:
        logger.error(f"Error converting SDF to XYZ: {str(e)}")
        return None

def download_structure(cid: str, format: str = 'sdf') -> str:
    """Download compound structure"""
    logger.info(f"Downloading structure: cid={cid}, format={format}")
    
    if not cid or not cid.strip():
        return "Error: CID cannot be empty"
    
    cid = cid.strip()
    
    # Build API URL
    format_lower = format.lower()
    if format_lower == 'sdf':
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d&response_type=save"
    else:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/{format_lower}/?response_type=save"
    
    try:
        session = create_session()
        response = session.get(url, timeout=180)
        response.raise_for_status()
        
        # Return structure data
        return response.text
    except Exception as e:
        logger.error(f"Error downloading structure: {str(e)}")
        return f"Error: Failed to download structure: {str(e)}"

def get_tools_list() -> List[Dict[str, Any]]:
    """Get list of available tools"""
    return [
        {
            "name": "get_pubchem_data",
            "description": "Retrieve compound structure and property data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Compound name or PubChem CID",
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format, options: 'JSON', 'CSV', or 'XYZ', default: 'JSON'",
                        "enum": ["JSON", "CSV", "XYZ"],
                    },
                    "include_3d": {
                        "type": "boolean",
                        "description": "Whether to include 3D structure information (only effective when format is 'XYZ'), default: false",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "download_structure",
            "description": "Download compound structure file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cid": {
                        "type": "string",
                        "description": "PubChem CID",
                    },
                    "format": {
                        "type": "string",
                        "description": "File format, options: 'sdf', 'mol', 'smi', default: 'sdf'",
                        "enum": ["sdf", "mol", "smi"],
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename to save as (optional)",
                    }
                },
                "required": ["cid"],
            },
        }
    ]

def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool call"""
    logger.info(f"Handling tool call: {tool_name}, arguments: {arguments}")
    
    if tool_name == "get_pubchem_data":
        query = arguments.get("query")
        format_type = arguments.get("format", "JSON")
        include_3d = arguments.get("include_3d", False)
        
        if not query:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Missing required parameter 'query'"
                    }
                ],
                "isError": True
            }
        
        # Validate that XYZ format requires include_3d parameter
        if format_type.upper() == "XYZ" and not include_3d:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "When using XYZ format, include_3d parameter must be set to true"
                    }
                ],
                "isError": True
            }
        
        try:
            result = get_pubchem_data(query, format_type, include_3d)
            
            # Check for errors
            if result.startswith("Error:"):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ],
                    "isError": True
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error executing get_pubchem_data: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    elif tool_name == "download_structure":
        cid = arguments.get("cid")
        format_type = arguments.get("format", "sdf")
        filename = arguments.get("filename")
        
        if not cid:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: Missing required parameter 'cid'"
                    }
                ],
                "isError": True
            }
        
        try:
            # Download structure
            structure_data = download_structure(cid, format_type)
            
            # Check for errors
            if structure_data.startswith("Error:"):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": structure_data
                        }
                    ],
                    "isError": True
                }
            
            # Determine filename
            if not filename:
                filename = f"pubchem_{cid}.{format_type.lower()}"
            
            # Save to file
            try:
                with open(filename, 'w') as f:
                    f.write(structure_data)
                
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Successfully saved structure to file: {filename}\n\n" + 
                                   f"Compound CID: {cid}\n" +
                                   f"File format: {format_type.upper()}\n" +
                                   f"File size: {len(structure_data)} bytes"
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Error saving file: {str(e)}")
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Failed to save file: {str(e)}"
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            logger.error(f"Error executing download_structure: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: Unknown tool: {tool_name}"
                }
            ],
            "isError": True
        }

def main():
    """Main function - MCP server entry point"""
    logger.info("PubChem MCP server started")
    
    while True:
        try:
            # Read a line
            line = sys.stdin.readline()
            if not line:
                logger.info("Input ended")
                break
                
            logger.debug(f"Received: {line.strip()}")
            
            # Parse request
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            
            logger.info(f"Processing request: method={method}, id={request_id}")
            
            # Handle different types of requests
            if method == "initialize":
                # Log client info
                client_info = params.get("clientInfo", {})
                client_name = client_info.get("name", "unknown")
                client_version = client_info.get("version", "unknown")
                protocol_version = params.get("protocolVersion", "unknown")
                logger.info(f"Client: {client_name} {client_version}, Protocol version: {protocol_version}")
                
                # Create correct initialization response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": protocol_version,
                        "serverInfo": {
                            "name": "pubchem-mcp-server",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
                
            elif method == "list_tools":
                logger.info("Processing tools list request")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": get_tools_list()
                    }
                }
                
            elif method == "call_tool":
                logger.info("Processing tool call request")
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    logger.warning("Missing tool name")
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                    }
                else:
                    result = handle_tool_call(tool_name, arguments)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
            
            # These methods may be used in some MCP clients
            elif method == "tools/list":
                logger.info("Processing tools/list request")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": get_tools_list()
                    }
                }
            
            elif method == "tools/call":
                logger.info("Processing tools/call request")
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    logger.warning("Missing tool name")
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                    }
                else:
                    result = handle_tool_call(tool_name, arguments)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
            
            else:
                logger.warning(f"Unknown method: {method}")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Serialize response
            response_json = json.dumps(response)
            logger.debug(f"Sending response: {response_json}")
            
            # Write to stdout and flush immediately
            sys.stdout.write(response_json + "\n")
            sys.stdout.flush()
            
            logger.info(f"Response sent: method={method}, id={request_id}")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"Unhandled exception: {e}")
            logger.error(traceback.format_exc())
            try:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id if 'request_id' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except:
                logger.error("Failed to send error response")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
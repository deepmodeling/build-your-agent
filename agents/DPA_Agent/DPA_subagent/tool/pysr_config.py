"""
Simple PySR configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Union, Optional


def load_pysr_config(config_path: str = "output/task_config_pysr.json") -> Dict:
    """Load PySR configuration from JSON file"""
    if not os.path.exists(config_path):
        # Default configuration
        default_config = {
            "unary_operators": ["exp=e^x", "log=log(x)", "sin=sin(x)", "cos=cos(x)", "sqrt=sqrt(x)"],
        }
        save_pysr_config(default_config, config_path)
        return default_config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_pysr_config(config: Dict, config_path: str = "output/task_config_pysr.json"):
    """Save PySR configuration to JSON file"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def create_pysr_config(
    unary_operators: List[str] = None,
    parameters: Optional[List[Union[float, str, int]]] = None,
    config_path: str = "output/task_config_pysr.json"
) -> Dict:
    """Create PySR configuration"""
    config = load_pysr_config(config_path)
    
    if unary_operators:
        config["unary_operators"] = unary_operators
    if parameters is not None:
        config["parameters"] = parameters
    
    save_pysr_config(config, config_path)
    return config


def set_unary_operators(unary_operators: List[str], config_path: str = "output/task_config_pysr.json"):
    """Set unary operators"""
    config = load_pysr_config(config_path)
    config["unary_operators"] = unary_operators
    save_pysr_config(config, config_path)


def set_binary_operators(binary_operators: List[str], config_path: str = "output/task_config_pysr.json"):
    """Set binary operators"""
    config = load_pysr_config(config_path)
    config["binary_operators"] = binary_operators
    save_pysr_config(config, config_path)




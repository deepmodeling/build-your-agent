"""
Utility Functions for NexusAgent Symbolic Regression

This module provides various utility functions for data processing, file I/O,
formula manipulation, and other common operations in the symbolic regression workflow.
"""

import ast
import json
import os
import pickle
import re
import logging
from typing import Dict, List, Union, Any
from pathlib import Path
import sympy as sp
import sympy
from sympy import sympify, preorder_traversal, Pow, exp, E
import pandas as pd
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

_BAD_LITERAL_RE = re.compile(r'(?:nan|inf|zoo)', re.I)


async def read_data(csv_path: str) -> Dict[str, List[float]]:
    """
    Read data from CSV or Excel file and return in dictionary format.
    
    Args:
        csv_path: Path to the data file (CSV or Excel format)
        
    Returns:
        Dictionary containing independent and dependent variable data
        Format: {variable_name_dependent: [values], dependent_var_independent: [values]}
        
    Raises:
        ValueError: If file type is not supported
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    
    try:
        if csv_path.endswith(".csv"):
            df = pd.read_csv(csv_path, header=0)
        elif csv_path.endswith(".xlsx"):
            df = pd.read_excel(csv_path, header=0)
        else:
            raise ValueError(f"Unsupported file type: {csv_path}. Only CSV and Excel files are supported.")
        
        # Return variables and dependent variable in dictionary format
        variables = df.columns.tolist()
        dependent_variable = variables[-1]
        independent_variables = variables[:-1]

        data = {}
        for variable in independent_variables:
            data[f"{variable}_dependent"] = df[variable].tolist()
        data[f"{dependent_variable}_independent"] = df[dependent_variable].tolist()
    
        return data
    
    except Exception as e:
        raise Exception(f"Failed to read data from {csv_path}: {e}")


async def write_txt(content: str, filename: str) -> str:
    """
    Write content to a text file in the output directory.
    
    Args:
        content: Content to write to file
        filename: Name of the output file
        
    Returns:
        Success message string
        
    Raises:
        Exception: If file writing fails
    """
    try:
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(content)
            
        return f"🎉 Successfully wrote content to {filename}"
    
    except Exception as e:
        raise Exception(f"Failed to write to {filename}: {e}")


async def write_data_description(content: str, filename: str) -> str:
    """
    Write data description content to a file in the data_description subdirectory.
    
    Args:
        content: Data description content to write
        filename: Name of the output file (without extension)
        
    Returns:
        Success message string
        
    Raises:
        Exception: If file writing fails
    """
    try:
        os.makedirs("output/data_description", exist_ok=True)
        filepath = f"output/data_description/{filename}.txt"
        
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(content)
            
        return f"🎉 Successfully wrote data description to {filename}"
    
    except Exception as e:
        raise Exception(f"Failed to write data description to {filename}: {e}")


def lisp_to_infix(expr: str) -> str:
    """
    Convert Lisp-style expressions to infix expressions (suitable for sympy).
    
    Args:
        expr: Lisp-style expression string
        
    Returns:
        Infix expression string
        
    Raises:
        ValueError: If expression is invalid or empty
    """
    import ast
    import operator

    ops = {
        '+': '+',
        '-': '-',
        '*': '*',
        '/': '/',
        '^': '**'
    }

    def tokenize(s):
        """Tokenize the expression string."""
        return s.replace('(', ' ( ').replace(')', ' ) ').split()

    def parse(tokens):
        """Parse tokens into nested list structure."""
        if not tokens:
            raise ValueError("Empty expression")
        token = tokens.pop(0)
        if token == '(':
            subexpr = []
            while tokens and tokens[0] != ')':
                subexpr.append(parse(tokens))
            if not tokens:
                raise ValueError("Mismatched parentheses")
            tokens.pop(0)  # pop ')'
            return subexpr
        else:
            return token

    def to_infix(parsed):
        """Convert parsed structure to infix notation."""
        if isinstance(parsed, str):
            return parsed
        if not parsed:
            raise ValueError("Empty parsed expression")
        op = parsed[0]
        args = parsed[1:]
        args = [to_infix(a) for a in args]
        return f"({f' {ops.get(op, op)} '.join(args)})"

    try:
        return to_infix(parse(tokenize(expr)))
    except Exception as e:
        raise ValueError(f"Failed to convert Lisp expression to infix: {e}")


def write_init_pop(content: str) -> str:
    """
    Write initial population formulas to a pickle file.
    
    Args:
        content: String representation of formula list or actual list
        
    Returns:
        Success message string
        
    Raises:
        Exception: If writing fails
    """
    try:
        # Try to parse as literal list first
        try:
            formulas = ast.literal_eval(content)
            if not isinstance(formulas, list):
                raise ValueError("Content is not a list")
        except Exception:
            # If literal_eval fails, try regex extraction
            formulas = re.findall(r'["\']([^"\']+)["\']', content)
            if not formulas:
                raise ValueError("No valid formulas found in content")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_formulas = []
        for formula in formulas:
            if formula not in seen:
                seen.add(formula)
                unique_formulas.append(formula)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        pickle_path = "output/init_pop.pkl"
        
        # Write or append to existing pickle file
        if not os.path.exists(pickle_path):
            with open(pickle_path, 'wb') as f:
                pickle.dump(unique_formulas, f)
        else:
            with open(pickle_path, 'rb') as f:
                existing_data = pickle.load(f)
            
            # Combine and deduplicate
            combined = existing_data + unique_formulas
            seen = set()
            final_formulas = []
            for formula in combined:
                if formula not in seen:
                    seen.add(formula)
                    final_formulas.append(formula)
            
            with open(pickle_path, 'wb') as f:
                pickle.dump(final_formulas, f)
        
        return f"🎉 Successfully wrote {len(unique_formulas)} formulas to initial population"
    
    except Exception as e:
        raise Exception(f"Failed to write initial population: {e}")


def validate_expression(expr: str) -> bool:
    """
    Validate if an expression string can be parsed by sympy.
    
    Args:
        expr: Expression string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        sympify(expr)
        return True
    except Exception:
        return False


def ensure_output_directory(subdir: str = "") -> Path:
    """
    Ensure output directory exists and return the path.
    
    Args:
        subdir: Optional subdirectory name
        
    Returns:
        Path object for the output directory
    """
    if subdir:
        output_path = Path("output") / subdir
    else:
        output_path = Path("output")
    
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_best_expression():
    """Get best expression"""
    try:
        with open("output/results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["candidates"]
    except:
        return None


def get_all_expressions():
    """
    Get all expression information from results.json
    
    Returns:
        Dict: Dictionary containing complete expression information, returns None if file doesn't exist
    """
    try:
        with open("output/results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.warning("results.json file not found")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse results.json: {e}")
        return None
    except Exception as e:
        logger.error(f"Error occurred while reading results.json: {e}")
        return None


def get_expression_summary():
    """
    Get brief summary information of expressions
    
    Returns:
        Dict: Dictionary containing expression count, best expression and other summary information
    """
    all_expressions = get_all_expressions()
    if not all_expressions:
        return None
    
    try:
        summary = {
            "total_expressions": len(all_expressions.get("equations", [])),
            "best_expression": all_expressions.get("candidates", "N/A"),
            "complexity_range": {
                "min": min([eq.get("complexity", 0) for eq in all_expressions.get("equations", [])]) if all_expressions.get("equations") else 0,
                "max": max([eq.get("complexity", 0) for eq in all_expressions.get("equations", [])]) if all_expressions.get("equations") else 0
            },
            "loss_range": {
                "min": min([eq.get("loss", float('inf')) for eq in all_expressions.get("equations", [])]) if all_expressions.get("equations") else 0,
                "max": max([eq.get("loss", float('inf')) for eq in all_expressions.get("equations", [])]) if all_expressions.get("equations") else 0
            }
        }
        return summary
    except Exception as e:
        logger.error(f"Error occurred while generating expression summary: {e}")
        return None
import numpy as np
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from pysr import PySRRegressor
from sklearn.preprocessing import StandardScaler
import sympy as sp
from typing import List
from .iteration_manager import register_pysr_results_tool
from .pysr_config import load_pysr_config



import re


def build_function_mappings(extra_map: dict) -> dict:

    base = {
        "square": lambda x: x**2,
        "cube":   lambda x: x**3,
        "cbrt":   lambda x: x**(1/3),
        "inv":    lambda x: 1/x,
        "neg":    lambda x: -x,
    }

    for name, expr_str in (extra_map or {}).items():
        try:
            if expr_str.strip().lower() == "builtin":
                continue
            x = sp.Symbol("x")
            base[name] = sp.lambdify(x, sp.sympify(expr_str), modules=["numpy", "sympy"])
        except Exception as e:
            print(f"[WARN] Failed to parse {name} in extra_sympy_mappings: {e}")
    return base

def calculate_complexity(expr_str: str) -> int:
    """Calculate expression complexity"""
    try:
        # Basic complexity calculation
        complexity = 0
        complexity += expr_str.count('+') + expr_str.count('-')  # Addition and subtraction
        complexity += expr_str.count('*') * 2 + expr_str.count('/') * 2  # Multiplication and division have higher weight
        complexity += expr_str.count('**') * 3  # Power operations have highest weight
        complexity += expr_str.count('(')  # Parentheses add complexity
        complexity += len([c for c in expr_str if c.isalpha()])  # Number of variables
        
        # Function calls add complexity
        functions = ['sin', 'cos', 'exp', 'log', 'sqrt', 'abs', 'neg']
        for func in functions:
            complexity += expr_str.count(func) * 2
            
        return max(1, complexity)  # Minimum complexity is 1
    except:
        return 1
    
def _simplify_expr(expr, sig=3) -> str:
    """
    Simplify PySR generated expressions to equivalent forms,
    and convert all coefficients to decimal with sig significant digits.
    """
    try:
        expr_str = str(expr)
        
        # Fix common syntax issues first
        # Don't remove any parentheses - let sympy handle the expression as is
        # expr_str = re.sub(r'\)(?![^(]*\()', '', expr_str)  # This was causing issues
        
        # Replace function calls with their equivalent forms
        expr_str = re.sub(r'square\(([^)]+)\)', r'(\1)**2', expr_str)
        expr_str = re.sub(r'cube\(([^)]+)\)',   r'(\1)**3', expr_str)
        expr_str = re.sub(r'cbrt\(([^)]+)\)',   r'(\1)**(1/3)', expr_str)
        expr_str = re.sub(r'inv\(([^)]+)\)',    r'1/(\1)', expr_str)
        expr_str = re.sub(r'neg\(([^)]+)\)',    r'-(\1)', expr_str)

        sym_expr = sp.sympify(expr_str, evaluate=True)
        sym_expr = sp.expand(sym_expr)
        sym_expr = sp.simplify(sym_expr)

        sym_expr = sp.nfloat(sym_expr, n=sig)   # SymPy ≥ 1.12

        result = str(sym_expr)
        
        # Handle double negative: - - becomes +
        # Use a simpler approach without look-behind assertions
        # First handle cases like "- -3.078537" -> "+ 3.078537"
        result = re.sub(r'(\s|^)-\s*-\s*(\d+\.?\d*)', r'\1+ \2', result)
        # Then handle general double negative cases
        result = re.sub(r'(\s|^)-\s*-\s*', r'\1+ ', result)
        # Handle cases where there might be spaces around the minus signs
        result = re.sub(r'(\s|^)-\s*-\s*(\w+)', r'\1+ \2', result)
        
        # Clean redundant operators and coefficients
        result = re.sub(r'\*\*1(\.0+)?', '', result)
        result = re.sub(r'\*1(\.0+)?(?=\W)', '', result)
        result = re.sub(r'(\W)1(\.0+)?\*', r'\1*', result)
        
        result = re.sub(r'\+\s*0(\.0+)?(?=\W|$)', '', result)
        result = re.sub(r'(\W|^)0(\.0+)?\s*\+', r'\1', result)
        
        # Clean extra spaces
        result = re.sub(r'\s+', ' ', result)

        return result.strip()

    except Exception as e:
        print(f"[WARN] _simplify_expr failed: {e}")
        return str(expr).strip("()")


async def run_symbolic_pysr(csv_path: str):
    config = load_pysr_config()

    function_mappings = build_function_mappings(config.get("extra_sympy_mappings", {}))

    df = pd.read_csv(csv_path)
    x_cols, y_col = df.columns[:-1], df.columns[-1]
    data_x, data_y = df[x_cols], df[y_col]

    model = PySRRegressor(
        niterations=1000,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=config["unary_operators"],
        extra_sympy_mappings=function_mappings,
        model_selection="best",
        elementwise_loss="loss(x, y) = (x - y)^2",  # Fix deprecated warning
        populations=50,
        procs=10,
        maxsize=20,
        maxdepth=5,
        verbosity=0,
        turbo=True,
    )
    model.fit(data_x, data_y)

    hof = model.get_hof()
    sub = hof.iloc[:, :3].copy()
    sub.iloc[:, 0] = sub.iloc[:, 2].apply(calculate_complexity)
    sub.iloc[:, 2] = sub.iloc[:, 2].apply(_simplify_expr)
    sub.columns = ["complexity","mse","expression"]
    sub.to_csv("output/best.txt", sep="\t", index=False, header=True)

    try:
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "csv_path": csv_path,
                "num_candidates": len(sub)
            },
            "candidates": [
                {
                    "complexity": int(row["complexity"]),
                    "mse": float(row["mse"]),
                    "expression": row["expression"]
                }
                for _, row in sub.iterrows()
            ]
        }
        if results["candidates"]:
            results["best_result"] = results["candidates"][0]
        
        with open("output/results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: JSON save failed: {e}")

    register_pysr_results_tool()

    # best_function = Path(f"output/best.txt").read_text().strip()
    return results

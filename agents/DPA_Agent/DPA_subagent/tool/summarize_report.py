"""
Summarize Report Tool

This module generates comprehensive analysis reports for symbolic regression results,
combining the best expressions with mechanism analysis and data descriptions.
"""

import ast
import os
import json
import re
from pathlib import Path
from typing import List, Optional, Union

# Ensure loading .env file
import DPA_subagent  # noqa: F401
from litellm import completion

from openai import AzureOpenAI
from DPA_subagent.prompt.agent_prompt import build_SUMMARIZE_PROMPT
from DPA_subagent.tool.iteration_manager import register_summary_report_tool
from DPA_subagent.tool.utils import get_best_expression



async def summarize_report() -> str:
    """
    Generate comprehensive analysis report using the latest OpenAI Python + Azure setup.
    
    This function reads mechanism tags, data descriptions, and best expressions,
    then generates a detailed analysis report combining all findings.
    
    Returns:
        str: Generated analysis report content
        
    Raises:
        FileNotFoundError: If required input files are missing
        Exception: If report generation fails
    """
    try:
        # Check and read mechanism tags
        # mechanism_tags_path = Path("output/mechanism_tags.txt")
        # if not mechanism_tags_path.exists():
        #     raise FileNotFoundError("mechanism_tags.txt not found in output directory")
        # mechanism_tags = mechanism_tags_path.read_text(encoding='utf-8').strip()
        
        # Check and read data description (try multiple possible locations)
        data_description = None

        data_description = Path(f"output/deepresearch_report.md").read_text().strip()
        
        # Check and read best expressions
        best_expressions = get_best_expression()
        if best_expressions:
            print(f"Best expression: {best_expressions}")
        else:
            print("No best expression found")


        # Generate the analysis report
        prompt = build_SUMMARIZE_PROMPT(best_expressions, data_description)

        response = completion(
            model=os.getenv("MODEL"),
            temperature=0,
            max_tokens=8192,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional in mathematical modeling and scientific analysis, "
                               "skilled at interpreting symbolic regression results and generating comprehensive reports."
                },
                {
                    "role": "user", 
                    "content": prompt
                },
            ],
        )

        content = response["choices"][0]["message"]["content"].strip()

        # Save the generated report
        output_path = Path("output/summarize.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Register summary report to iteration history
        try:
            result = register_summary_report_tool(content)
            print(f"Summary report registration result: {result}")
        except Exception as e:
            print(f"Error occurred when registering summary report: {e}")

        return content
        
    except FileNotFoundError as e:
        error_msg = f"Required input file missing: {e}"
        # Save error message to output for debugging
        with open("output/summarize_error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        raise FileNotFoundError(error_msg)
        
    except Exception as e:
        error_msg = f"Failed to generate analysis report: {e}"
        with open("output/summarize_error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        raise Exception(error_msg)
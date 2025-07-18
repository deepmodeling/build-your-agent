from DPA_subagent.tool.task_manager import get_task_status, get_task_result
from DPA_subagent.tool.pysr import run_symbolic_pysr
from DPA_subagent.tool.pysr_config import set_unary_operators,set_binary_operators
from DPA_subagent.tool.summarize_report import summarize_report
from DPA_subagent.tool.iteration_manager import iteration_manager
from DPA_subagent.tool.deepresearch import deepresearch_agent
from pathlib import Path

async def run_symbolic_tool_pysr(csv_path: str):
    """
    run symbolic regression with pysr
    Args:
        csv_path: str, the path of the csv file
    Returns:
        result: str, the result of the symbolic regression
        the different columns are:
            complexity: the complexity of the expression
            mse: the mse of the expression
            expression: the expression

        you should save the result to a variable with the key `symbolic_result`

    """
    result = await run_symbolic_pysr(csv_path=csv_path)
    return result

def get_task_status_tool(task_id: str):
    """
    get the status of the task
    Args:
        task_id: str, the id of the task
    Returns:
        status: str, the status of the task
    """
    return get_task_status(task_id)


def get_task_result_tool(task_id: str):
    """
    get the result of the task
    Args:
        task_id: str, the id of the task
    Returns:
        result: str, the result of the task
    """
    return get_task_result(task_id)


async def summarize_report_tool():
    """
    summarize the report
    
    return: str, the summarize report
    """
    report = await summarize_report()
    return report


async def set_unary_operators_tool(unary_operators: list[str]):
    """
    set the pysr unary operators
    Args:
        unary_operators: list, the unary operators
        the value is the unary operator name
        [str, str]
        you can only use the operators in the following list, do not use any other operators.
        ["exp", "log", "sin", "cos", "sqrt","inv","square","cube","abs","sign","log1p"]
    Returns:
        "success set unary operators"
    example:
        unary_operators = ["exp", "log", "sin", "cos", "sqrt"]
    """
    set_unary_operators(unary_operators)

    return f"success set unary operators: {unary_operators}"





async def generate_data_description_tool(data_description: str):
    """
    generate the data description
    Args:
        data_description: str, user request, must be comprehensive and detailed
    Returns:
        the report of the data description
    example:
        data_description = "The data is about the relationship between the age and the height of the students,x1 is the age,x2 is the height"
        generate_data_description_tool(data_description)
    """
    #mock the data description
    data_description_report = await deepresearch_agent(data_description)
    return data_description_report


async def write_summarize_report_tool(report: str):
    """
    write the summarize report to a file
    Args:
        report: str, the report content
    Returns:
        "success write summarize report"
    """
    with open("output/summarize_report.md", "w") as f:
        f.write(report)
    return "success write summarize report"




def get_iteration_history_tool():
    """
    Get iteration history for refine_agent analysis
    Returns:
        str: History summary
    """
    return iteration_manager.get_history_summary()


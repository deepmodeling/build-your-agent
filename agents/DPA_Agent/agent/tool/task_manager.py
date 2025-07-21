import threading
import uuid
from typing import Callable, Dict, Optional

# Internal task status management
_TASK_STORE = {}
_ERROR_CACHE = {}
_RESULT_CACHE = {}


def submit_task(func: Callable[[], str]) -> str:
    """
    Submit a background task (sync function), return task ID immediately.
    
    Args:
        func: function without parameters, returns str (execution result)
    
    Returns:
        task_id: for querying task status or result
    """
    task_id = str(uuid.uuid4())
    
    def worker():
        try:
            result = func()
            _RESULT_CACHE[task_id] = result
            _TASK_STORE[task_id] = "completed"
        except Exception as e:
            _ERROR_CACHE[task_id] = str(e)
            _TASK_STORE[task_id] = "failed"
    
    _TASK_STORE[task_id] = "running"
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    return task_id


def get_task_status(task_id: str) -> str:
    """
    Query task status.
    
    Returns:
        str: "✅ Completed" / "❌ Failed: ..." / "⏳ Running" / "❓ Unknown task"
    """
    if _TASK_STORE.get(task_id) == "completed":
        return "✅ Completed"
    elif _TASK_STORE.get(task_id) == "failed":
        return f"❌ Failed: {_ERROR_CACHE[task_id]}"
    elif _TASK_STORE.get(task_id) == "running":
        return "⏳ Running"
    else:
        return "❓ Unknown task"


def get_task_result(task_id: str) -> Optional[str]:
    """
    Get task result (if completed).
    """
    if _TASK_STORE.get(task_id) == "completed":
        return _RESULT_CACHE.get(task_id, "No result")
    return "Task not completed or failed"


def get_task_error(task_id: str) -> Optional[str]:
    """
    Get task failure information (if any).
    """
    return _ERROR_CACHE.get(task_id, "No error information")
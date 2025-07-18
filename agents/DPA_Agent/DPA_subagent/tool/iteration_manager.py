"""
Iteration History Manager
Record configuration, results and summary for each round
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
from DPA_subagent.tool.pysr_config import load_pysr_config
from DPA_subagent.tool.utils import get_best_expression, get_all_expressions, get_expression_summary

class IterationHistory:
    """Single iteration history record"""
    def __init__(self, round_num: int, config: Dict = None, 
                 pysr_results: Dict = None, summary_report: str = None, 
                 timestamp: str = None):
        self.round_num = round_num
        self.config = config or {}
        self.pysr_results = pysr_results  # Store complete PySR results
        self.summary_report = summary_report  # Store summary report
        self.timestamp = timestamp or datetime.now().isoformat()


class IterationManager:
    """Iteration manager"""
    
    def __init__(self, history_file: str = "output/iteration_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
    
    def load_history(self) -> List[IterationHistory]:
        """Load history records"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history = []
            for item in data:
                # Compatible with old format
                if 'best_results' in item:
                    # Old format conversion
                    history.append(IterationHistory(
                        round_num=item['round_num'],
                        config=item.get('config', {}),
                        pysr_results={'best_results': item['best_results']},
                        summary_report=item.get('summary', ''),
                        timestamp=item['timestamp']
                    ))
                else:
                    # New format
                    history.append(IterationHistory(
                        round_num=item['round_num'],
                        config=item.get('config', {}),
                        pysr_results=item.get('pysr_results', {}),
                        summary_report=item.get('summary_report', ''),
                        timestamp=item['timestamp']
                    ))
            
            return history
        except Exception as e:
            print(f"Failed to load history records: {e}")
            return []
    
    def save_history(self, history: List[IterationHistory]):
        """Save history records"""
        try:
            data = []
            for item in history:
                data.append({
                    'round_num': item.round_num,
                    'config': item.config,
                    'pysr_results': item.pysr_results,
                    'summary_report': item.summary_report.replace("\\n", "\n") if isinstance(item.summary_report, str) else item.summary_report,
                    'timestamp': item.timestamp
                })
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Failed to save history records: {e}")
    
    def register_pysr_results(self, config: Dict = None) -> int:
        """
        Register PySR results
        
        Args:
            config: PySR configuration, if None then auto-load
            
        Returns:
            int: Round number
        """
        try:
            if config is None:
                config = load_pysr_config()
            
            all_expressions = get_all_expressions()
            if all_expressions is None:
                print("Warning: results.json file not found")
                all_expressions = {}
            
            history = self.load_history()
            round_num = len(history) + 1
            
            existing_iteration = None
            for item in history:
                if item.round_num == round_num:
                    existing_iteration = item
                    break
            
            if existing_iteration:
                existing_iteration.config = config
                existing_iteration.pysr_results = all_expressions
                existing_iteration.timestamp = datetime.now().isoformat()
            else:
                new_iteration = IterationHistory(
                    round_num=round_num,
                    config=config,
                    pysr_results=all_expressions,
                    summary_report=None
                )
                history.append(new_iteration)
            
            self.save_history(history)
            return round_num
            
        except Exception as e:
            print(f"Failed to register PySR results: {e}")
            return -1
    
    def register_summary_report(self, summary_report: str, round_num: int = None) -> int:
        """
        Register summary report
        
        Args:
            summary_report: Summary report content
            round_num: Specified round number, if None then use current round
            
        Returns:
            int: Round number
        """
        try:
            history = self.load_history()
            
            if round_num is None:
                round_num = len(history)  
            
            target_iteration = None
            for item in history:
                if item.round_num == round_num:
                    target_iteration = item
                    break
            
            if target_iteration:
                target_iteration.summary_report = summary_report
                target_iteration.timestamp = datetime.now().isoformat()
            else:
                new_iteration = IterationHistory(
                    round_num=round_num,
                    config={},
                    pysr_results={},
                    summary_report=summary_report
                )
                history.append(new_iteration)
                history.sort(key=lambda x: x.round_num)
            
            self.save_history(history)
            return round_num
            
        except Exception as e:
            print(f"Failed to register summary report: {e}")
            return -1
    
    def get_current_round(self) -> int:
        """Get current round"""
        history = self.load_history()
        return len(history)
    
    def get_pysr_completion_round(self) -> int:
        """
        Query PySR task completion round
        
        Returns:
            int: Number of rounds with completed PySR tasks, return 0 if none completed
        """
        history = self.load_history()
        completed_rounds = 0
        
        for item in history:
            if item.pysr_results and item.pysr_results != {}:
                completed_rounds = max(completed_rounds, item.round_num)
        
        return completed_rounds
    
    def get_summary_completion_round(self) -> int:
        """
        Query summary report completion round
        
        Returns:
            int: Number of rounds with completed summary reports, return 0 if none completed
        """
        history = self.load_history()
        completed_rounds = 0
        
        for item in history:
            if item.summary_report and item.summary_report.strip():
                completed_rounds = max(completed_rounds, item.round_num)
        
        return completed_rounds
    
    def get_round_status(self, round_num: int = None) -> Dict:
        """
        Get completion status for specified round
        
        Args:
            round_num: Round number, if None then get current round
            
        Returns:
            Dict: Dictionary containing completion status for each task
        """
        if round_num is None:
            round_num = self.get_current_round()
        
        history = self.load_history()
        target_iteration = None
        
        for item in history:
            if item.round_num == round_num:
                target_iteration = item
                break
        
        if not target_iteration:
            return {
                "round_num": round_num,
                "pysr_completed": False,
                "summary_completed": False,
                "config_set": False
            }
        
        return {
            "round_num": round_num,
            "pysr_completed": bool(target_iteration.pysr_results and target_iteration.pysr_results != {}),
            "summary_completed": bool(target_iteration.summary_report and target_iteration.summary_report.strip()),
            "config_set": bool(target_iteration.config and target_iteration.config != {}),
            "timestamp": target_iteration.timestamp
        }
    
    def get_history_summary(self) -> str:
        """Get history summary for prompt"""
        history = self.load_history()
        
        if not history:
            return "This is the first iteration, no history available."
        
        summary_parts = []
        summary_parts.append(f"Completed {len(history)} iterations:\n")
        
        for item in history:
            summary_parts.append(f"=== Round {item.round_num} ===")
            summary_parts.append(f"Configuration: {item.config}")
            
            # Show PySR results summary
            if item.pysr_results and 'candidates' in item.pysr_results:
                eq_count = len(item.pysr_results['candidates'])
                summary_parts.append(f"PySR results: {eq_count} expressions")
            else:
                summary_parts.append("PySR results: Not completed")
            
            # Show summary report status
            if item.summary_report and item.summary_report.strip():
                summary_parts.append(f"Summary report: {item.summary_report[:150]}...")
            else:
                summary_parts.append("Summary report: Not completed")
            
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def clear_history(self):
        """Clear history records"""
        if self.history_file.exists():
            self.history_file.unlink()


# Global instance
iteration_manager = IterationManager() 


 
def register_pysr_results_tool() -> str:
    """
    Register PySR results
    
    Returns:
        str: Registration result information
    """
    try:
        round_num = iteration_manager.register_pysr_results()
        return f"Successfully registered PySR results for round {round_num}"
    except Exception as e:
        return f"Failed to register PySR results: {e}"


def register_summary_report_tool(summary_report: str, round_num: int = None) -> str:
    """
    Register summary report
    
    Args:
        summary_report: Summary report content
        round_num: Specified round number, if None then use current round
        
    Returns:
        str: Registration result information
    """
    try:
        actual_round = iteration_manager.register_summary_report(summary_report, round_num)
        return f"Successfully registered summary report for round {actual_round}"
    except Exception as e:
        return f"Failed to register summary report: {e}"


def get_task_status() -> str:
    """
    Get task completion status
    
    Returns:
        str: Task status information
    """
    try:
        current_round = iteration_manager.get_current_round()
        pysr_round = iteration_manager.get_pysr_completion_round()
        summary_round = iteration_manager.get_summary_completion_round()
        
        status_info = [
            f"Current round: {current_round}",
            f"PySR task completed through round {pysr_round}",
            f"Summary report completed through round {summary_round}"
        ]
        
        if current_round > 0:
            current_status = iteration_manager.get_round_status(current_round)
            status_info.append(f"Round {current_round} status:")
            status_info.append(f"  - PySR: {'✓' if current_status['pysr_completed'] else '✗'}")
            status_info.append(f"  - Summary report: {'✓' if current_status['summary_completed'] else '✗'}")
            status_info.append(f"  - Configuration: {'✓' if current_status['config_set'] else '✗'}")
        
        return "\n".join(status_info)
        
    except Exception as e:
        return f"Failed to get task status: {e}"
    

def get_pysr_task_status() -> str:
    """
    Get PySR task completion status
    
    Returns:
        str: Task status information
    """
    pysr_round = iteration_manager.get_pysr_completion_round()
    return f"PySR task completed through round {pysr_round}"


def get_summary_task_status() -> str:
    """
    Get summary report completion status
    
    Returns:
        str: Task status information
    """
    summary_round = iteration_manager.get_summary_completion_round()
    return f"Summary report completed through round {summary_round}"

"""Logging utilities"""

from datetime import datetime
from pathlib import Path


class Logger:
    """Log all output to file"""
    
    def __init__(self, log_file: str = "./vol.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def log_command_output(self, task: str, cmd: str, output: str, success: bool):
        self.log(f"{'SUCCESS' if success else 'FAILED'}: {task}")
        self.log(f"  Command: {cmd}")
        if output.strip():
            for line in output.strip().split("\n"):
                self.log(f"  | {line}")

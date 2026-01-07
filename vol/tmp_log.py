"""Temporary log file management for static output"""

import os
from pathlib import Path
from typing import Optional

# Default temp log file
DEFAULT_TMP_LOG = ".vol.tmp"

# Global temp log instance
_tmp_log: Optional["TmpLog"] = None


class TmpLog:
    """Manage temporary log file for static output.
    
    In "speed mode" - we show output inline immediately.
    With tmp log - we save static output to file and redraw on panel open/close.
    """
    
    def __init__(self, path: str = DEFAULT_TMP_LOG):
        self.path = Path(path)
        self.lines: list[str] = []
        # Clear file on init
        self.clear()
    
    def clear(self):
        """Clear the temp log file"""
        self.lines = []
        try:
            self.path.write_text("")
        except Exception:
            pass
    
    def add_line(self, line: str):
        """Add a line to the temp log"""
        self.lines.append(line)
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
    
    def get_lines(self) -> list[str]:
        """Get all lines from the temp log"""
        return self.lines.copy()
    
    def read_from_file(self) -> list[str]:
        """Read lines from the temp log file"""
        if self.path.exists():
            try:
                content = self.path.read_text(encoding="utf-8")
                self.lines = content.splitlines()
                return self.lines.copy()
            except Exception:
                pass
        return []
    
    def cleanup(self):
        """Remove the temp log file"""
        try:
            if self.path.exists():
                self.path.unlink()
        except Exception:
            pass


def get_tmp_log() -> TmpLog:
    """Get or create the global temp log instance"""
    global _tmp_log
    if _tmp_log is None:
        _tmp_log = TmpLog()
    return _tmp_log


def init_tmp_log(path: str = DEFAULT_TMP_LOG):
    """Initialize the temp log with a path"""
    global _tmp_log
    _tmp_log = TmpLog(path)
    return _tmp_log


def log_static_line(line: str):
    """Log a static output line to the temp log"""
    get_tmp_log().add_line(line)

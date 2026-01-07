"""Temporary log file management for static output"""

import os
import atexit
from pathlib import Path
from typing import Optional

# Default temp log file base
DEFAULT_TMP_LOG_BASE = ".vol"
DEFAULT_TMP_LOG_EXT = ".tmp"

# Global temp log instance
_tmp_log: Optional["TmpLog"] = None


def find_available_tmp_path() -> Path:
    """Find an available tmp log file path (.vol.tmp, .vol2.tmp, .vol3.tmp, ...)"""
    base_path = Path(f"{DEFAULT_TMP_LOG_BASE}{DEFAULT_TMP_LOG_EXT}")
    if not base_path.exists():
        return base_path
    
    # Find next available number
    n = 2
    while True:
        path = Path(f"{DEFAULT_TMP_LOG_BASE}{n}{DEFAULT_TMP_LOG_EXT}")
        if not path.exists():
            return path
        n += 1


class TmpLog:
    """Manage temporary log file for static output.
    
    In "speed mode" - we show output inline immediately.
    With tmp log - we save static output to file and redraw on panel open/close.
    """
    
    def __init__(self, path: Path = None):
        if path is None:
            path = find_available_tmp_path()
        self.path = path
        self.lines: list[str] = []
        # Create empty file to reserve the name
        self._create_file()
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def _create_file(self):
        """Create the temp log file"""
        try:
            self.path.write_text("")
        except Exception:
            pass
    
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


def init_tmp_log() -> TmpLog:
    """Initialize the temp log with an available path"""
    global _tmp_log
    _tmp_log = TmpLog()
    return _tmp_log


def log_static_line(line: str):
    """Log a static output line to the temp log"""
    get_tmp_log().add_line(line)


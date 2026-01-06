"""
Volumes v2 (vol) - Universal build tool with beautiful output
https://github.com/pluttan/volumes
"""

from .output import console, print_status
from .config import VolConfig
from .runner import VolRunner, run_command_with_output
from .script import parse_script, run_script
from .makefile import parse_makefile, run_makefile, list_makefile_targets
from .logger import Logger

__version__ = "2.0.0"
__all__ = [
    "console",
    "print_status",
    "VolConfig",
    "VolRunner",
    "run_command_with_output",
    "parse_script",
    "run_script",
    "parse_makefile",
    "run_makefile",
    "list_makefile_targets",
    "Logger",
]


"""Output formatting and console utilities"""

import sys
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.text import Text

console = Console()

# Status labels
STATUS_LABELS = {
    "wait": "WAIT",
    "ok": "OK",
    "warn": "WARN",
    "error": "ERROR",
    "info": "INFO",
}

# Padding to align all labels to same width (ERROR is 5 chars)
STATUS_WIDTHS = {
    "wait": 1,   # WAIT  = 4 chars, need 1 space
    "ok": 3,     # OK    = 2 chars, need 3 spaces  
    "warn": 1,   # WARN  = 4 chars, need 1 space
    "error": 0,  # ERROR = 5 chars, need 0 spaces
    "info": 1,   # INFO  = 4 chars, need 1 space
}


def get_status_color(status: str) -> str:
    """Get color for status from theme config"""
    from .config import get_ui_config
    ui = get_ui_config()
    theme = ui.theme
    
    colors = {
        "wait": theme.wait,
        "ok": theme.ok,
        "warn": theme.warn,
        "error": theme.error,
        "info": theme.info,
    }
    return colors.get(status, "white")



def clear_screen():
    """Clear terminal screen"""
    import os
    os.system('clear')


def clear_line():
    """Clear current line (move up and clear)"""
    sys.stdout.write("\033[1A\033[2K")
    sys.stdout.flush()


def get_terminal_height() -> int:
    """Get terminal height in rows"""
    return console.size.height


def setup_terminal_for_progress():
    """Clear screen and add padding to push content to bottom"""
    from .config import get_ui_config
    ui = get_ui_config()
    
    if ui.clear_screen:
        clear_screen()
    
    if ui.bottom_up:
        height = get_terminal_height()
        padding = height - 1
        if padding > 0:
            for _ in range(padding):
                console.print()


# Max length for task name column
MAX_TASK_NAME_LEN = 6

def set_max_task_name_length(length: int):
    """Set maximum length for task name column"""
    global MAX_TASK_NAME_LEN
    MAX_TASK_NAME_LEN = max(6, length)  # maintain at least 6 chars


def format_task_name(task_name: str) -> str:
    """Format task name with brackets and padding"""
    # Truncate if longer than max
    if len(task_name) > MAX_TASK_NAME_LEN:
        short_name = task_name[:MAX_TASK_NAME_LEN]
    else:
        short_name = task_name
    
    bracketed = f"[{short_name}]"
    # Pad to MAX_TASK_NAME_LEN + 2 brackets
    padded = bracketed.ljust(MAX_TASK_NAME_LEN + 2)
    return f" {padded}"


def print_status(status: str, message: str, time_str: Optional[str] = None, task_name: Optional[str] = None):
    """Print formatted status line: [STATUS] [TIME] [TASK] message"""
    from .config import get_ui_config
    ui = get_ui_config()
    
    if time_str is None:
        time_str = datetime.now().strftime("%H:%M:%S")
    
    color = get_status_color(status)
    label = STATUS_LABELS.get(status, status.upper())
    padding = " " * STATUS_WIDTHS.get(status, 0)
    
    from rich.syntax import Syntax
    from rich.table import Table
    
    grid = Table.grid(padding=(0, 2))
    
    status_text = Text()
    
    # Status label [OK]/[WAIT] etc
    if ui.show_status_label:
        status_text.append(f"[{label}]", style=f"bold {color}")
        status_text.append(f"{padding}", style="dim")
    
    # Time
    if ui.show_time:
        status_text.append(f" [{time_str}]", style="bold dim")
    
    # Task name
    if ui.show_task_name and task_name:
        formatted_task = format_task_name(task_name)
        status_text.append(formatted_task, style="bold cyan")
    
    # Detect if message is a shell command or plain text description
    shell_indicators = ['echo ', 'sleep ', 'cd ', 'make ', 'mkdir ', 'rm ', 'cp ', 'mv ', 
                        'cat ', 'grep ', 'sed ', 'awk ', 'find ', 'ls ', 'pwd', 'export ',
                        'source ', 'pip ', 'python ', 'npm ', 'node ', 'git ', 'docker ',
                        '|', '&', '>', '<', ';', '$(', '`', '&&', '||']
    
    is_shell = any(message.startswith(ind) or ind in message for ind in shell_indicators)
    
    if is_shell:
        syntax = Syntax(message, "bash", theme=ui.syntax_theme, background_color="default", word_wrap=True)
        grid.add_row(status_text, syntax)
    else:
        status_text.append(f"  {message}", style="bold")
        grid.add_row(status_text)
    
    console.print(grid)
    
    # Log static output (non-WAIT statuses) to tmp log for redraw
    if status != "wait":
        from .tmp_log import get_tmp_log
        from io import StringIO
        from rich.console import Console as RichConsole
        
        # Capture output with ANSI colors
        string_io = StringIO()
        temp_console = RichConsole(file=string_io, force_terminal=True, width=console.width)
        temp_console.print(grid)
        ansi_line = string_io.getvalue().rstrip('\n')
        get_tmp_log().add_line(ansi_line)



def print_header():
    """Print header if enabled in config"""
    from .config import get_ui_config
    ui = get_ui_config()
    
    if ui.show_header:
        console.print()
        console.print(f"[bold]{ui.header_text}[/bold]", style=ui.theme.header)
        console.print()


def print_error_footer():
    """Print error footer message if enabled in config"""
    from .config import get_ui_config
    ui = get_ui_config()
    
    if ui.show_footer and ui.show_error_message:
        console.print()
        print_status("info", ui.error_message)



def redraw_from_tmp_log():
    """Clear screen and redraw static output from .vol.tmp file.
    
    This is called when opening/closing command output panels to
    restore the static output (OK/ERROR lines) from the tmp log.
    """
    from .config import get_ui_config
    from .tmp_log import get_tmp_log
    
    ui = get_ui_config()
    tmp_log = get_tmp_log()
    
    # Read lines from tmp log
    lines = tmp_log.get_lines()
    
    # Clear screen first
    if ui.clear_screen:
        clear_screen()
    
    # Calculate content height including header (3 lines if shown)
    header_height = 3 if ui.show_header else 0
    content_height = len(lines) + header_height
    
    # For bottom_up mode, add padding to push content to bottom of screen
    height = get_terminal_height()
    padding = max(0, height - content_height - 1)
    
    # Print padding lines first
    if padding > 0:
        sys.stdout.write("\n" * padding)
        sys.stdout.flush()
    
    # Print header after padding
    if ui.show_header:
        console.print()
        console.print(f"[bold]{ui.header_text}[/bold]", style=ui.theme.header)
        console.print()
    
    # Print all saved lines with ANSI colors preserved
    for line in lines:
        # Lines already contain ANSI codes, use sys.stdout directly
        sys.stdout.write(line + "\n")
    sys.stdout.flush()


def log_static_output(line: str):
    """Log a static output line to the tmp log file.
    
    This saves the formatted status line so it can be redrawn
    when command output panels are opened/closed.
    """
    from .tmp_log import get_tmp_log
    get_tmp_log().add_line(line)


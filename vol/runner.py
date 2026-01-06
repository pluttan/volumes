"""Command execution and task running"""

import os
import sys
import subprocess
from datetime import datetime

from rich.panel import Panel
from rich.live import Live
from rich import box

from .output import console, print_status
from .buffer import OutputBuffer
from .logger import Logger
from .config import VolConfig, expand_env_vars


def run_command_with_output(cmd: str, description: str, ignore_errors: bool, logger: Logger, task_name: str = None) -> bool:
    """
    Run command with live context window showing output (last 10 lines).
    Shows Live display only if command takes longer than 100ms.
    Returns True if successful.
    """
    import time
    from rich.console import Group
    from rich.text import Text
    from .progress import get_progress
    from .config import get_ui_config
    
    ui_config = get_ui_config()
    
    start_time = datetime.now().strftime("%H:%M:%S")
    start_timestamp = time.time()
    PANEL_WIDTH = ui_config.panel_width
    # Account for panel border (2 chars each side) and padding
    content_width = PANEL_WIDTH - 6 if PANEL_WIDTH > 6 else PANEL_WIDTH
    buffer = OutputBuffer(
        max_lines=ui_config.panel_height,
        max_width=content_width,
        wrap_lines=ui_config.wrap_lines
    )
    DELAY_MS = ui_config.delay_ms
    
    # Expand environment variables in command  
    cmd = expand_env_vars(cmd)
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        
        full_output = []
        progress = get_progress()
        
        # Create description header
        from .output import STATUS_WIDTHS
        from rich.table import Table
        from rich.syntax import Syntax
        
        padding = " " * STATUS_WIDTHS.get("wait", 0)
        
        desc_grid = Table.grid(padding=(0, 2))
        
        status_text = Text()
        
        # Status label
        if ui_config.show_status_label:
            status_text.append("[WAIT]", style="bold blue")
            status_text.append(f"{padding}", style="dim")
        
        # Time
        if ui_config.show_time:
            status_text.append(f" [{start_time}]", style="bold dim")
        
        # Task name
        if ui_config.show_task_name and task_name:
             from .output import format_task_name
             formatted_task = format_task_name(task_name)
             status_text.append(formatted_task, style="bold cyan")
        
        # Detect if description is a shell command or plain text
        shell_indicators = ['echo ', 'sleep ', 'cd ', 'make ', 'mkdir ', 'rm ', 'cp ', 'mv ', 
                            'cat ', 'grep ', 'sed ', 'awk ', 'find ', 'ls ', 'pwd', 'export ',
                            'source ', 'pip ', 'python ', 'npm ', 'node ', 'git ', 'docker ',
                            '|', '&', '>', '<', ';', '$(', '`', '&&', '||']
        
        is_shell = any(description.startswith(ind) or ind in description for ind in shell_indicators)
        
        if is_shell:
            cmd_syntax = Syntax(description, "bash", theme=ui_config.syntax_theme, background_color="default", word_wrap=True)
            desc_grid.add_row(status_text, cmd_syntax)
        else:
            status_text.append(f"  {description}", style="bold")
            desc_grid.add_row(status_text)
        
        # Wait for DELAY_MS to see if command finishes quickly
        while (time.time() - start_timestamp) * 1000 < DELAY_MS:
            if process.poll() is not None:
                break
            time.sleep(0.01)
        
        # Collect any output that came during wait using select
        import select
        
        while True:
            # Check if there's data to read (timeout=0 for non-blocking)
            readable, _, _ = select.select([process.stdout], [], [], 0)
            if not readable:
                break
            line = process.stdout.readline()
            if not line:
                break
            full_output.append(line)
            buffer.add_line(line)
        
        # If process still running OR progress bar is active, use Live display
        if process.poll() is None or progress is not None:
            with Live(console=console, refresh_per_second=15, transient=True) as live:
                # Build initial components with panel if any output already
                initial_components = [desc_grid]
                
                if buffer.line_count() > 0:
                    panel = Panel(
                        buffer.get_display(),
                        box=box.ROUNDED,
                        border_style=ui_config.theme.panel_border,
                        padding=(0, 1),
                        width=PANEL_WIDTH,
                    )
                    initial_components.append(panel)
                
                if progress is not None:
                    from rich.table import Table
                    progress_table = Table.grid(padding=(0, 2))
                    bar_width = 15
                    
                    row = []
                    tasks = progress.tasks
                    theme = ui_config.theme
                    
                    # Build list of (task, color, show) tuples
                    bars_to_show = []
                    if len(tasks) > 1:
                        # Sub bar first (index 1), then Main bar (index 0)
                        if ui_config.show_sub_progress:
                            bars_to_show.append((tasks[1], theme.sub_bar))
                        if ui_config.show_main_progress:
                            bars_to_show.append((tasks[0], theme.main_bar))
                    else:
                        if ui_config.show_main_progress:
                            bars_to_show.append((tasks[0], theme.main_bar))
                        
                    for task, color in bars_to_show:
                        completed = task.completed
                        total = task.total or 1
                        percentage = completed / total
                        filled = int(bar_width * percentage)
                        empty = bar_width - filled
                        bar_str = f"[{color}]{'━' * filled}[/{color}][dim]{'━' * empty}[/dim]"
                        row.append(bar_str)
                        row.append(f" {int(completed)}/{int(total)}")
                    
                    if row:
                        progress_table.add_row(*row)
                        initial_components.append(progress_table)
                initial_components.append(Text("\033[J"))
                live.update(Group(*initial_components))
                
                while True:
                    # Non-blocking read
                    readable, _, _ = select.select([process.stdout], [], [], 0.05)
                    
                    if readable:
                        line = process.stdout.readline()
                        if line:
                            full_output.append(line)
                            buffer.add_line(line)
                        else:
                            # EOF
                            break
                    else:
                        if process.poll() is not None:
                            break
                    
                    # Build display components
                    components = [desc_grid]
                    
                    # Only add panel if there's output
                    if buffer.line_count() > 0:
                        panel = Panel(
                            buffer.get_display(),
                            box=box.ROUNDED,
                            border_style=ui_config.theme.panel_border,
                            padding=(0, 1),
                            width=PANEL_WIDTH,
                        )
                        components.append(panel)
                    
                    # Add progress bar if active
                    if progress is not None:
                        from rich.table import Table
                        progress_table = Table.grid(padding=(0, 2))
                        bar_width = 15
                        
                        row = []
                        tasks = progress.tasks
                        theme = ui_config.theme
                        
                        bars_to_show = []
                        if len(tasks) > 1:
                            if ui_config.show_sub_progress:
                                bars_to_show.append((tasks[1], theme.sub_bar))
                            if ui_config.show_main_progress:
                                bars_to_show.append((tasks[0], theme.main_bar))
                        else:
                            if ui_config.show_main_progress:
                                bars_to_show.append((tasks[0], theme.main_bar))
                            
                        for task, color in bars_to_show:
                            completed = task.completed
                            total = task.total or 1
                            percentage = completed / total
                            filled = int(bar_width * percentage)
                            empty = bar_width - filled
                            bar_str = f"[{color}]{'━' * filled}[/{color}][dim]{'━' * empty}[/dim]"
                            row.append(bar_str)
                            row.append(f" {int(completed)}/{int(total)}")
                        
                        if row:
                            progress_table.add_row(*row)
                            components.append(progress_table)
                    
                    # Add clear to end of screen
                    components.append(Text("\033[J"))
                    display = Group(*components)
                    live.update(display)
                # Live handles cleanup with transient=True
        else:
            # Process finished quickly, just read remaining output
            for line in process.stdout:
                full_output.append(line)
                buffer.add_line(line)
        
        return_code = process.wait()
        output_text = "".join(full_output)
        
        logger.log_command_output(description, cmd, output_text, return_code == 0)
        
        if return_code == 0:
            print_status("ok", description, start_time, task_name)
            return True
        else:
            if ignore_errors:
                print_status("warn", f"{description} (код {return_code})", start_time, task_name)
                return True
            else:
                print_status("error", f"{description} (код {return_code})", start_time, task_name)
                return False
                
    except Exception as e:
        logger.log(f"EXCEPTION: {description} - {e}")
        print_status("error", f"{description} ({e})", start_time, task_name)
        return False



class VolRunner:
    """Execute tasks from configuration"""
    
    def __init__(self, config: VolConfig):
        self.config = config
        self.logger = Logger(config.log_file)
    
    def run_task(self, task_name: str) -> bool:
        """Run a single task with all its steps"""
        task = self.config.get_task(task_name)
        if not task:
            print_status("error", f"Задача '{task_name}' не найдена")
            return False
        
        # Get commands - can be list of strings or list of dicts with description
        commands = task.get("commands", [])
        default_desc = task.get("description", task_name)
        ignore_errors = task.get("ignore_errors", False)
        
        for item in commands:
            if isinstance(item, dict):
                # Command with custom description: {cmd = "...", desc = "..."}
                cmd = expand_env_vars(item.get("cmd", ""))
                desc = item.get("desc", default_desc)
                cmd_ignore = item.get("ignore_errors", ignore_errors)
            else:
                # Simple string command
                cmd = expand_env_vars(str(item))
                desc = default_desc
                cmd_ignore = ignore_errors
            
            if not cmd:
                continue
                
            success = run_command_with_output(cmd, desc, cmd_ignore, self.logger)
            if not success and not cmd_ignore:
                print_status("info", f"Подробности в логе: {self.config.log_file}")
                return False
        
        return True
    
    def run_with_deps(self, task_name: str, extra_args: list[str] = None) -> bool:
        """Run task with all its dependencies"""
        # Inject extra args as environment variables
        if extra_args:
            import os
            for arg in extra_args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    os.environ[key] = value
        
        tasks_to_run = self.config.resolve_dependencies(task_name)
        
        if not tasks_to_run:
            print_status("error", f"Задача '{task_name}' не найдена")
            return False
        
        for name in tasks_to_run:
            if not self.run_task(name):
                return False
        
        return True

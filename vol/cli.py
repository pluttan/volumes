"""Command-line interface"""

import sys
import glob
import argparse
from pathlib import Path

from rich.table import Table
from rich import box

from .output import console, print_status, print_header, print_error_footer, clear_screen, setup_terminal_for_progress
from .config import VolConfig, UIConfig, set_ui_config
from .runner import VolRunner
from .script import run_script
from .makefile import list_makefile_targets, run_makefile
from .logger import Logger


def list_tasks(config: VolConfig):
    """Display all available tasks, scripts, and Makefile targets"""
    tasks = config.get_all_tasks()
    scripts = glob.glob("*.sh")
    toml_files = [f for f in glob.glob("*.toml") if f != "vol.toml"]
    makefile_targets = list_makefile_targets()
    
    if not tasks and not scripts and not toml_files and not makefile_targets:
        print_status("info", "Нет задач или скриптов")
        return
    
    table = Table(title="Доступные задачи", box=box.ROUNDED)
    table.add_column("Имя", style="cyan bold")
    table.add_column("Тип", style="dim")
    table.add_column("Описание", style="white")
    table.add_column("Зависимости", style="dim")
    
    # Add TOML tasks from current config
    for name, task in tasks.items():
        desc = task.get("description", "-")
        deps = ", ".join(task.get("depends", [])) or "-"
        table.add_row(name, "task", desc, deps)
    
    # Add Makefile targets
    for name, target in makefile_targets.items():
        desc = target.get("description", "-")
        deps = ", ".join(target.get("depends", [])) or "-"
        table.add_row(f"make:{name}", "make", desc, deps)
    
    # Add scripts
    for script in sorted(scripts):
        table.add_row(script, "script", "-", "-")
    
    # Add other TOML configs
    for toml in sorted(toml_files):
        table.add_row(f"-c {toml}", "config", f"vol -c {toml} --list", "-")
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        prog="vol",
        description="Volumes v2 - Universal build tool with beautiful output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vol build              Run 'build' task from vol.toml
  vol make:build         Run 'build' target from Makefile
  vol test               Run 'test' task (with dependencies)
  vol script.sh          Run shell script with volumes syntax
  vol --list             Show all available tasks
  vol -c app.toml build  Use custom config file
        """
    )
    
    parser.add_argument("task", nargs="?", help="Task name, make:<target>, or script file")
    parser.add_argument("-c", "--config", default="vol.toml", help="Config file (default: vol.toml)")
    parser.add_argument("-l", "--list", action="store_true", help="List all tasks")
    parser.add_argument("-v", "--version", action="version", version="vol 2.0.6")
    
    # Use parse_known_args to allow passing extra args to commands (e.g. VERSION=2.0.0)
    args, extra_args = parser.parse_known_args()
    
    # Load config early to get UI settings
    config_path = Path(args.config)
    if config_path.exists():
        config = VolConfig(args.config)
    else:
        # Use default UI config
        set_ui_config(UIConfig())
        config = None
    
    # Auto-detect if task is a script file
    if args.task and Path(args.task).is_file():
        script_path = args.task
        
        # Load inline config BEFORE printing header
        from .inline_config import load_config_from_script
        load_config_from_script(script_path)
        
        # Clear screen and prepare for bottom-up output (after config loaded)
        setup_terminal_for_progress()
        
        print_header()
        
        log_file = config.log_file if config else "./vol.log"
        logger = Logger(log_file)
        success = run_script(script_path, logger, extra_args)
        
        if not success:
            print_error_footer()
            sys.exit(1)
        return
    
    # Handle Makefile targets (make:target)
    if args.task and args.task.startswith("make:"):
        target_name = args.task[5:]  # Remove "make:" prefix
        
        # Load inline config from Makefile BEFORE printing header
        from .inline_config import load_config_from_makefile
        load_config_from_makefile()
        
        # Clear screen and prepare for bottom-up output (after config loaded)
        setup_terminal_for_progress()
        
        print_header()
        
        success = run_makefile(target_name, extra_args)
        
        if not success:
            print_error_footer()
            sys.exit(1)
        return
    
    # Create empty config if doesn't exist but we need to list
    if config is None:
        config = VolConfig.__new__(VolConfig)
        config.tasks = {}
        config.ui = UIConfig()
    
    if args.list:
        list_tasks(config)
        return
    
    if not args.task:
        parser.print_help()
        console.print("\n")
        list_tasks(config)
        return
    
    # Check if task exists in config
    if not config_path.exists():
        print_status("error", f"Конфигурация не найдена: {args.config}")
        console.print("\n[dim]Создайте vol.toml, используйте 'vol script.sh' или 'vol make:<target>'[/dim]")
        sys.exit(1)
    
    # Run task
    runner = VolRunner(config)
    
    print_header()
    
    success = runner.run_with_deps(args.task, extra_args)
    
    if not success:
        print_error_footer()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Shell script parsing and execution"""

import subprocess
from .output import print_status
from .runner import run_command_with_output
from .logger import Logger


def parse_script(filename: str) -> list[tuple[str, str, bool, bool]]:
    """
    Parse shell script with volumes syntax.
    
    Syntax:
    - `command # message` - run with critical failure
    - `command ## message` - run with non-critical failure (ignore errors)
    - `{ commands } # message` - multi-line block with description
    - `{ commands }` - multi-line block, silent (no output)
    - Lines starting with # are comments (skipped)
    
    Returns list of (command, description, ignore_errors, silent)
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    commands = []
    pos = 0
    length = len(content)

    while pos < length:
        # Skip whitespace and comment-only lines
        while pos < length and content[pos] in " \t\n":
            pos += 1
        
        if pos >= length:
            break
        
        # Skip comment lines (lines starting with #)
        if content[pos] == "#":
            # Check if this is a standalone comment (not part of a command)
            line_start = content.rfind("\n", 0, pos) + 1
            if content[line_start:pos].strip() == "":
                # This is a comment line, skip to end of line
                while pos < length and content[pos] != "\n":
                    pos += 1
                continue

        # Handle blocks { }
        if content[pos] == "{":
            end_pos = content.find("}", pos)
            if end_pos == -1:
                raise ValueError("Unclosed block in braces")

            cmd = content[pos+1:end_pos].strip()
            pos = end_pos + 1

            # Look for comment after block
            desc_pos = pos
            while desc_pos < length and content[desc_pos] in " \t":
                desc_pos += 1
            
            if desc_pos < length and content[desc_pos] == "#":
                # Find end of line
                line_end = content.find("\n", desc_pos)
                if line_end == -1:
                    line_end = length
                comment = content[desc_pos+1:line_end].strip()
                
                # Check for ## (ignore errors)
                if comment.startswith("#"):
                    description = comment[1:].strip()
                    ignore = True
                else:
                    description = comment
                    ignore = False
                pos = line_end
                silent = False
            else:
                # No comment = silent execution
                description = ""
                ignore = False
                silent = True

            commands.append((cmd, description, ignore, silent))

        # Handle regular commands
        else:
            line_end = content.find("\n", pos)
            if line_end == -1:
                line = content[pos:].strip()
                pos = length
            else:
                line = content[pos:line_end].strip()
                pos = line_end

            if not line or line.startswith("#"):
                continue

            if "#" in line:
                # Find the first # that's not inside quotes
                parts = line.split("#", 1)
                cmd = parts[0].strip()
                comment = parts[1].strip()
                
                # Check for ## (ignore errors)  
                if comment.startswith("#"):
                    description = comment[1:].strip()
                    ignore = True
                else:
                    description = comment
                    ignore = False
                silent = False
            else:
                cmd = line
                description = cmd[:40] + "..." if len(cmd) > 40 else cmd
                ignore = False
                silent = False

            if cmd:
                commands.append((cmd, description, ignore, silent))

    return commands


def run_script(filename: str, logger: Logger) -> bool:
    """Run a shell script with volumes syntax"""
    from .inline_config import load_config_from_script
    from .progress import create_progress, advance_progress, stop_progress
    
    # Try to load inline config from script
    load_config_from_script(filename)
    
    try:
        commands = parse_script(filename)
    except Exception as e:
        print_status("error", f"Ошибка парсинга скрипта: {e}")
        return False
    
    if not commands:
        print_status("warn", "Скрипт не содержит команд")
        return True
    import os
    script_name = os.path.basename(filename)
    from .output import set_max_task_name_length
    set_max_task_name_length(len(script_name))
    
    # Create progress bar
    create_progress(len(commands), f"Скрипт ({len(commands)} команд)")
    
    try:
        for i, (cmd, desc, ignore, silent) in enumerate(commands):
            if silent:
                # Silent execution - no status output
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                logger.log_command_output(desc or cmd[:30], cmd, result.stdout + result.stderr, result.returncode == 0)
                if result.returncode != 0 and not ignore:
                    return False
            else:
                # Extract script basename for task name
                import os
                script_name = os.path.basename(filename)
                success = run_command_with_output(cmd, desc, ignore, logger, script_name)
                if not success and not ignore:
                    return False
            
            advance_progress(1, f"{i+1}/{len(commands)}")
    finally:
        stop_progress()
    
    return True


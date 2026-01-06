"""Makefile parsing and execution"""

import re
import subprocess
from pathlib import Path

from .output import print_status
from .runner import run_command_with_output
from .logger import Logger


def find_matching_paren(text: str, start: int) -> int:
    """Find the matching closing parenthesis, handling nested parens"""
    depth = 0
    for i, char in enumerate(text[start:]):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return start + i
    return -1


def expand_make_functions(text: str) -> str:
    """Expand all GNU Make function calls like $(shell ...), $(word ...), etc."""
    result = text
    max_iterations = 100  # Prevent infinite loops
    
    for _ in range(max_iterations):
        # Find innermost function call first (to handle nesting)
        # Look for $(func where func is a known function name
        functions = ['shell', 'word', 'words', 'firstword', 'lastword', 
                     'subst', 'patsubst', 'strip', 'sort', 'dir', 'notdir',
                     'suffix', 'basename', 'addsuffix', 'addprefix', 'wildcard']
        
        found = False
        for func in functions:
            pattern = f'$({func} '
            idx = result.find(pattern)
            if idx != -1:
                end = find_matching_paren(result, idx + 1)  # +1 to skip $
                if end > idx:
                    full_expr = result[idx:end + 1]
                    inner = result[idx + len(pattern):end]
                    
                    # Recursively expand inner content first
                    inner = expand_make_functions(inner)
                    
                    # Now evaluate the function
                    value = evaluate_make_function(func, inner)
                    result = result[:idx] + value + result[end + 1:]
                    found = True
                    break
        
        if not found:
            break
    
    return result


def evaluate_make_function(func: str, args: str) -> str:
    """Evaluate a single Make function"""
    
    if func == 'shell':
        try:
            proc = subprocess.run(
                args.strip(),
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return proc.stdout.strip()
        except Exception:
            return ""
    
    elif func == 'word':
        # $(word n,text) - returns nth word (1-indexed)
        parts = args.split(',', 1)
        if len(parts) == 2:
            try:
                n = int(parts[0].strip())
                words = parts[1].strip().split()
                if 1 <= n <= len(words):
                    return words[n - 1]
            except (ValueError, IndexError):
                pass
        return ""
    
    elif func == 'words':
        # $(words text) - returns number of words
        return str(len(args.strip().split()))
    
    elif func == 'firstword':
        # $(firstword text) - returns first word
        words = args.strip().split()
        return words[0] if words else ""
    
    elif func == 'lastword':
        # $(lastword text) - returns last word
        words = args.strip().split()
        return words[-1] if words else ""
    
    elif func == 'subst':
        # $(subst from,to,text) - substitutes text
        parts = args.split(',', 2)
        if len(parts) == 3:
            from_str = parts[0]
            to_str = parts[1]
            text = parts[2]
            return text.replace(from_str, to_str)
        return args
    
    elif func == 'patsubst':
        # $(patsubst pattern,replacement,text) - pattern substitution with %
        parts = args.split(',', 2)
        if len(parts) == 3:
            pattern = parts[0].strip()
            replacement = parts[1].strip()
            text = parts[2].strip()
            
            words = text.split()
            result = []
            for word in words:
                if '%' in pattern:
                    # Pattern matching with %
                    prefix = pattern.split('%')[0]
                    suffix = pattern.split('%')[1] if '%' in pattern else ''
                    if word.startswith(prefix) and word.endswith(suffix):
                        stem = word[len(prefix):len(word) - len(suffix) if suffix else None]
                        new_word = replacement.replace('%', stem)
                        result.append(new_word)
                    else:
                        result.append(word)
                else:
                    if word == pattern:
                        result.append(replacement)
                    else:
                        result.append(word)
            return ' '.join(result)
        return args
    
    elif func == 'strip':
        # $(strip text) - removes leading/trailing whitespace, collapses internal
        return ' '.join(args.split())
    
    elif func == 'sort':
        # $(sort list) - sorts words and removes duplicates
        words = args.strip().split()
        return ' '.join(sorted(set(words)))
    
    elif func == 'dir':
        # $(dir names) - extracts directory part
        words = args.strip().split()
        return ' '.join(str(Path(w).parent) + '/' if '/' in w else './' for w in words)
    
    elif func == 'notdir':
        # $(notdir names) - extracts non-directory part
        words = args.strip().split()
        return ' '.join(Path(w).name for w in words)
    
    elif func == 'suffix':
        # $(suffix names) - extracts suffix
        words = args.strip().split()
        return ' '.join(Path(w).suffix for w in words if Path(w).suffix)
    
    elif func == 'basename':
        # $(basename names) - removes suffix
        words = args.strip().split()
        return ' '.join(str(Path(w).with_suffix('')) for w in words)
    
    elif func == 'addsuffix':
        # $(addsuffix suffix,names)
        parts = args.split(',', 1)
        if len(parts) == 2:
            suffix = parts[0]
            words = parts[1].strip().split()
            return ' '.join(w + suffix for w in words)
        return args
    
    elif func == 'addprefix':
        # $(addprefix prefix,names)
        parts = args.split(',', 1)
        if len(parts) == 2:
            prefix = parts[0]
            words = parts[1].strip().split()
            return ' '.join(prefix + w for w in words)
        return args
    
    elif func == 'wildcard':
        # $(wildcard pattern) - expands to matching files
        import glob
        matches = glob.glob(args.strip())
        return ' '.join(matches)
    
    return ""


def expand_variables(text: str, variables: dict) -> str:
    """Expand Make variables $(VAR) or ${VAR} in text"""
    # First expand all Make functions
    text = expand_make_functions(text)
    
    def replace_var(match):
        var_name = match.group(1) or match.group(2)
        return variables.get(var_name, match.group(0))
    
    # Match $(VAR) or ${VAR} - simple variable names only
    pattern = r'\$\(([A-Za-z_][A-Za-z0-9_]*)\)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}'
    return re.sub(pattern, replace_var, text)



def parse_variable_line(line: str) -> tuple[str, str] | None:
    """Parse a variable assignment line. Returns (name, value) or None."""
    # Match VAR := value or VAR = value or VAR ?= value
    match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*[:?]?=\s*(.*)$', line.strip())
    if match:
        return match.group(1), match.group(2).strip()
    return None


def parse_command(cmd_line: str) -> tuple[str, str, bool, bool]:
    """
    Parse a Makefile command line.
    
    Returns (command, description, silent, is_info)
    - command: the actual command to run (empty if info-only)
    - description: comment after # or the command itself
    - silent: True if command starts with @
    - is_info: True if this is just a comment (info message, no command)
    """
    # Check for @ prefix (silent)
    silent = cmd_line.startswith("@")
    if silent:
        cmd_line = cmd_line[1:]
    
    # Check for inline comment
    if "#" in cmd_line:
        # Split at first #
        parts = cmd_line.split("#", 1)
        cmd = parts[0].strip()
        description = parts[1].strip()
        # If command is empty but has description, this is an info line
        is_info = (cmd == "" and description != "")
    else:
        cmd = cmd_line.strip()
        description = cmd  # Use command itself as description
        is_info = False
    
    return cmd, description, silent, is_info


def parse_makefile(filename: str = "Makefile") -> dict[str, dict]:
    """
    Parse Makefile and extract targets with commands and descriptions.
    
    Syntax:
    - `# Description` before target - used as target description
    - `target: [deps]` - target definition
    - `target: [deps] ## Description` - inline target description
    - `\\t<command>` - commands (lines starting with tab)
    - `\\t<command> # description` - command with inline description
    - `\\t@<command>` - silent command (no echo)
    
    Returns dict of {target_name: {"description": str, "depends": list, "commands": list}}
    Commands are tuples of (cmd, description, silent)
    
    Returns (targets_dict, variables_dict)
    """
    with open(filename, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
    
    # Preprocess: join continuation lines (ending with \)
    lines = []
    current_line = ""
    for line in raw_lines:
        stripped_end = line.rstrip()
        if stripped_end.endswith("\\"):
            # Continuation - append without backslash and newline
            current_line += stripped_end[:-1]
        else:
            current_line += line
            lines.append(current_line)
            current_line = ""
    if current_line:
        lines.append(current_line)
    
    targets = {}
    variables = {}
    current_description = None
    current_target = None
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines in target context, reset description
        if not stripped:
            if current_target is None:
                current_description = None
            continue
        
        # Comment before target = description
        if stripped.startswith("#") and not line.startswith("\t"):
            # Check if it's a description comment (not a directive like #!)
            comment = stripped[1:].strip()
            if comment and not comment.startswith("!") and not comment.startswith("-"):
                current_description = comment
            continue
        
        # Variable assignment (VAR := value or VAR = value)
        var_result = parse_variable_line(stripped)
        if var_result and not line.startswith("\t"):
            var_name, var_value = var_result
            # Expand variables in the value
            var_value = expand_variables(var_value, variables)
            variables[var_name] = var_value
            continue
        
        # Target definition: name: [deps]  ## optional description
        target_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)$', line.rstrip())
        if target_match and not line.startswith("\t"):
            target_name = target_match.group(1)
            rest = target_match.group(2)
            
            # Check for inline description (## comment)
            if "##" in rest:
                deps_part, desc = rest.split("##", 1)
                deps = [d.strip() for d in deps_part.split() if d.strip()]
                description = desc.strip()
            else:
                deps = [d.strip() for d in rest.split() if d.strip()]
                description = current_description or target_name
            
            targets[target_name] = {
                "description": description,
                "depends": deps,
                "commands": [],
            }
            current_target = target_name
            current_description = None
            continue
        
        # Command (starts with tab)
        if line.startswith("\t") and current_target:
            cmd_line = line[1:].rstrip()  # Remove leading tab
            if cmd_line:
                cmd, desc, silent, is_info = parse_command(cmd_line)
                if cmd or is_info:  # Include info-only lines
                    targets[current_target]["commands"].append({
                        "cmd": cmd,
                        "desc": desc,
                        "silent": silent,
                        "is_info": is_info,
                    })
            continue
        
        # Anything else resets the current target
        current_target = None
    
    return targets, variables


def run_makefile_target(target_name: str, targets: dict, variables: dict, logger: Logger, executed: set = None) -> bool:
    """Run a Makefile target with its dependencies"""
    from .progress import advance_progress
    
    if executed is None:
        executed = set()
    
    if target_name in executed:
        return True
    
    if target_name not in targets:
        print_status("error", f"Цель '{target_name}' не найдена в Makefile")
        return False
    
    target = targets[target_name]
    
    # Run dependencies first
    for dep in target["depends"]:
        if dep in targets:  # Only run if it's a defined target
            if not run_makefile_target(dep, targets, variables, logger, executed):
                return False
    
    # Run commands
    from .progress import create_sub_progress, remove_sub_progress, advance_sub_progress
    
    cmds = target["commands"]
    if cmds:
        create_sub_progress(len(cmds), f"{target_name}")
    
    try:
        for cmd_info in cmds:
            cmd = cmd_info["cmd"]
            desc = cmd_info["desc"]
            is_info = cmd_info.get("is_info", False)
            silent = cmd_info.get("silent", False)
            
            # Expand Make variables in cmd and desc
            if cmd:
                cmd = expand_variables(cmd, variables)
            desc = expand_variables(desc, variables)
            
            if is_info:
                # Info-only line - only print if not silent
                if not silent:
                    print_status("info", desc)
            else:
                # Run command - silently if @ prefixed
                if silent:
                    # Silent mode - run without status output
                    import subprocess
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    logger.log_command_output(desc, cmd, result.stdout + result.stderr, result.returncode == 0)
                    if result.returncode != 0:
                        return False
                else:
                    success = run_command_with_output(cmd, desc, False, logger, target_name)
                    if not success:
                        return False
            
            # Advance progress bars
            advance_progress(1)
            advance_sub_progress(1)
            
    finally:
        remove_sub_progress()
    
    executed.add(target_name)
    return True


def run_makefile(target_name: str, extra_args: list[str] = None, makefile: str = "Makefile") -> bool:
    """Run a target from a Makefile"""
    from .inline_config import load_config_from_makefile
    from .progress import create_progress, advance_progress, stop_progress
    
    if not Path(makefile).exists():
        print_status("error", f"Makefile не найден: {makefile}")
        return False
    
    # Try to load inline config from Makefile
    load_config_from_makefile(makefile)
    
    try:
        targets, variables = parse_makefile(makefile)
        
        # Override variables from extra_args (e.g. VERSION=2.0.1)
        if extra_args:
            for arg in extra_args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    variables[key] = value
                    
    except Exception as e:
        print_status("error", f"Ошибка парсинга Makefile: {e}")
        return False
    
    if not targets:
        print_status("warn", "Makefile не содержит целей")
        return True
    
    if target_name not in targets:
        print_status("error", f"Цель '{target_name}' не найдена")
        print_status("info", f"Доступные цели: {', '.join(targets.keys())}")
        return False
    
    # Count total commands across all targets to be executed
    def count_commands(name: str, visited: set) -> int:
        if name in visited or name not in targets:
            return 0
        visited.add(name)
        target = targets[name]
        count = len(target["commands"])
        for dep in target["depends"]:
            count += count_commands(dep, visited)
        return count
    
    visited_targets = set()
    total_cmds = count_commands(target_name, visited_targets)
    
    if visited_targets:
        max_len = max(len(t) for t in visited_targets)
        from .output import set_max_task_name_length
        set_max_task_name_length(max_len)
    
    logger = Logger("./vol.log")
    
    if total_cmds > 0:
        create_progress(total_cmds, f"make:{target_name}")
    
    try:
        return run_makefile_target(target_name, targets, variables, logger)
    finally:
        stop_progress()


def list_makefile_targets(makefile: str = "Makefile") -> dict[str, dict]:
    """Get all targets from a Makefile"""
    if not Path(makefile).exists():
        return {}
    
    try:
        targets, _ = parse_makefile(makefile)
        return targets
    except:
        return {}


"""Inline config parsing for scripts and Makefiles"""

import tomllib
from typing import Optional

from .config import UIConfig, set_ui_config


def parse_inline_config(content: str, comment_prefix: str = "#") -> Optional[dict]:
    """
    Parse inline TOML config from file content.
    
    For shell scripts:
        #--config:
        #log_file = "./vol.log"
        #show_header = false
        #[theme]
        #ok = "bright_green"
        #--end
    
    For Makefile:
        #--config:
        #log_file = "./vol.log"
        #show_header = false
        #[theme]
        #ok = "bright_green"
        #--end
    
    Returns parsed TOML dict or None if no config found.
    """
    config_start = f"{comment_prefix}--config:"
    config_end = f"{comment_prefix}--end"
    
    # Find config block
    start_idx = content.find(config_start)
    if start_idx == -1:
        return None
    
    end_idx = content.find(config_end, start_idx)
    if end_idx == -1:
        return None
    
    # Extract config lines
    config_block = content[start_idx + len(config_start):end_idx]
    
    # Remove comment prefixes from each line
    lines = []
    for line in config_block.split("\n"):
        stripped = line.strip()
        if stripped.startswith(comment_prefix):
            # Remove the comment prefix
            lines.append(stripped[len(comment_prefix):])
        elif stripped == "":
            lines.append("")
    
    toml_content = "\n".join(lines)
    
    try:
        return tomllib.loads(toml_content)
    except Exception:
        return None


def apply_inline_config(content: str, comment_prefix: str = "#") -> bool:
    """
    Parse and apply inline config from file content.
    Returns True if config was found and applied.
    """
    config_dict = parse_inline_config(content, comment_prefix)
    if config_dict is None:
        return False
    
    ui_config = UIConfig.from_dict(config_dict)
    set_ui_config(ui_config)
    return True


def load_config_from_script(filename: str) -> bool:
    """Load inline config from a shell script"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return apply_inline_config(content, "#")
    except:
        return False


def load_config_from_makefile(filename: str = "Makefile") -> bool:
    """Load inline config from a Makefile"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return apply_inline_config(content, "#")
    except:
        return False

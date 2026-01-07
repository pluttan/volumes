"""TOML configuration parsing with theme support"""

import os
import tomllib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


def expand_env_vars(value: str) -> str:
    """Expand environment variables in string ($HOME, ${VAR}, etc.)"""
    return os.path.expandvars(value)


# Default configuration
DEFAULT_CONFIG = {
    "log_file": "./vol.log",
    "show_header": True,
    "show_error_message": True,
    "header_text": "෴ Volumes v2 ෴",
    "error_message": "Выполнение прервано из-за ошибки",
    "theme": {
        "wait": "blue",
        "ok": "green",
        "warn": "yellow",
        "error": "red",
        "info": "cyan",
        "header": "cyan",
    }
}


# Built-in color theme presets (hex or rich color names)
COLOR_PRESETS = {
    "default": {
        "wait": "blue",
        "ok": "green", 
        "warn": "yellow",
        "error": "red",
        "info": "cyan",
        "header": "cyan",
        "main_bar": "green",
        "sub_bar": "blue",
        "panel_border": "blue",
    },
    "catppuccin": {
        "wait": "#89b4fa",      # Blue
        "ok": "#a6e3a1",        # Green
        "warn": "#f9e2af",      # Yellow
        "error": "#f38ba8",     # Red
        "info": "#94e2d5",      # Teal
        "header": "#cba6f7",    # Mauve
        "main_bar": "#a6e3a1",  # Green
        "sub_bar": "#89b4fa",   # Blue
        "panel_border": "#6c7086",  # Overlay0
    },
    "monokai": {
        "wait": "#66d9ef",      # Cyan
        "ok": "#a6e22e",        # Green
        "warn": "#e6db74",      # Yellow
        "error": "#f92672",     # Red/Pink
        "info": "#ae81ff",      # Purple
        "header": "#fd971f",    # Orange
        "main_bar": "#a6e22e",  # Green
        "sub_bar": "#66d9ef",   # Cyan
        "panel_border": "#75715e",  # Comment
    },
    "dracula": {
        "wait": "#8be9fd",      # Cyan
        "ok": "#50fa7b",        # Green
        "warn": "#f1fa8c",      # Yellow
        "error": "#ff5555",     # Red
        "info": "#bd93f9",      # Purple
        "header": "#ff79c6",    # Pink
        "main_bar": "#50fa7b",  # Green
        "sub_bar": "#8be9fd",   # Cyan
        "panel_border": "#6272a4",  # Comment
    },
    "nord": {
        "wait": "#81a1c1",      # Frost
        "ok": "#a3be8c",        # Green
        "warn": "#ebcb8b",      # Yellow
        "error": "#bf616a",     # Red
        "info": "#88c0d0",      # Frost light
        "header": "#b48ead",    # Purple
        "main_bar": "#a3be8c",  # Green
        "sub_bar": "#81a1c1",   # Frost
        "panel_border": "#4c566a",  # Polar night
    },
}


@dataclass
class Theme:
    """Color theme for status messages"""
    wait: str = "blue"
    ok: str = "green"
    warn: str = "yellow"
    error: str = "red"
    info: str = "cyan"
    header: str = "cyan"
    main_bar: str = "green"
    sub_bar: str = "blue"
    panel_border: str = "blue"
    
    @classmethod
    def from_dict(cls, data: dict, preset_name: str = None) -> "Theme":
        # Start with preset if specified
        if preset_name and preset_name in COLOR_PRESETS:
            base = COLOR_PRESETS[preset_name].copy()
        else:
            base = COLOR_PRESETS["default"].copy()
        
        # Override with explicit values from data
        base.update({k: v for k, v in data.items() if v is not None})
        
        return cls(
            wait=base.get("wait", "blue"),
            ok=base.get("ok", "green"),
            warn=base.get("warn", "yellow"),
            error=base.get("error", "red"),
            info=base.get("info", "cyan"),
            header=base.get("header", "cyan"),
            main_bar=base.get("main_bar", "green"),
            sub_bar=base.get("sub_bar", "blue"),
            panel_border=base.get("panel_border", "blue"),
        )


@dataclass
class UIConfig:
    """UI display configuration"""
    # Screen setup
    clear_screen: bool = True
    bottom_up: bool = True
    
    # Speed mode: True = fast (no redraw), False = slow (redraw from .vol.tmp on panel open/close)
    speed_mode: bool = False
    
    # Header/Footer
    show_header: bool = True
    show_footer: bool = True
    header_text: str = "🔨 Make Build"
    error_message: str = "Выполнение прервано из-за ошибки"
    
    # Progress bars
    show_main_progress: bool = True
    show_sub_progress: bool = True
    
    # Status line components
    show_status_label: bool = True
    show_time: bool = True
    show_task_name: bool = True
    
    # Syntax highlighting
    syntax_theme: str = "ansi_dark"
    
    # Output panel
    panel_width: int = 60          # Ширина панели вывода
    panel_height: int = 10         # Максимальная высота (строк)
    wrap_lines: bool = True        # Переносить строки (False = резать)
    delay_ms: int = 100            # Задержка перед появлением панели (мс)
    
    # Logging
    log_file: str = "./vol.log"
    
    # Legacy alias
    show_error_message: bool = True
    
    # Color theme preset (catppuccin, monokai, dracula, nord, default)
    color_theme: str = "default"
    
    theme: Theme = field(default_factory=Theme)

    
    @classmethod
    def from_dict(cls, data: dict) -> "UIConfig":
        theme_data = data.get("theme", {})
        color_theme = data.get("color_theme", "default")
        return cls(
            clear_screen=data.get("clear_screen", True),
            bottom_up=data.get("bottom_up", True),
            speed_mode=data.get("speed_mode", False),
            show_header=data.get("show_header", True),
            show_footer=data.get("show_footer", True),
            header_text=data.get("header_text", "🔨 Make Build"),
            error_message=data.get("error_message", "Выполнение прервано из-за ошибки"),
            show_main_progress=data.get("show_main_progress", True),
            show_sub_progress=data.get("show_sub_progress", True),
            show_status_label=data.get("show_status_label", True),
            show_time=data.get("show_time", True),
            show_task_name=data.get("show_task_name", True),
            syntax_theme=data.get("syntax_theme", "ansi_dark"),
            panel_width=data.get("panel_width", 60),
            panel_height=data.get("panel_height", 10),
            wrap_lines=data.get("wrap_lines", True),
            delay_ms=data.get("delay_ms", 100),
            log_file=expand_env_vars(data.get("log_file", "./vol.log")),
            show_error_message=data.get("show_error_message", True),
            color_theme=color_theme,
            theme=Theme.from_dict(theme_data, preset_name=color_theme),
        )



# Global UI config instance
_ui_config: Optional[UIConfig] = None


def get_ui_config() -> UIConfig:
    """Get current UI configuration"""
    global _ui_config
    if _ui_config is None:
        _ui_config = UIConfig()
    return _ui_config


def set_ui_config(config: UIConfig):
    """Set UI configuration"""
    global _ui_config
    _ui_config = config


class VolConfig:
    """Parse and manage vol.toml configuration"""
    
    def __init__(self, config_path: str = "vol.toml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.tasks = {}
        self.ui = UIConfig()
        
        if self.config_path.exists():
            self.load()
        
        # Apply UI config globally
        set_ui_config(self.ui)
    
    @property
    def log_file(self) -> str:
        return self.ui.log_file
    
    def load(self):
        with open(self.config_path, "rb") as f:
            self.config = tomllib.load(f)
        
        # Get config section (renamed from settings)
        config_section = self.config.get("config", self.config.get("settings", {}))
        self.ui = UIConfig.from_dict(config_section)
        
        # Parse tasks (everything except config/settings)
        self.tasks = {}
        for key, value in self.config.items():
            if key in ("config", "settings"):
                continue
            if isinstance(value, dict):
                self.tasks[key] = value
    
    def get_task(self, name: str) -> Optional[dict]:
        return self.tasks.get(name)
    
    def get_all_tasks(self) -> dict:
        return self.tasks
    
    def resolve_dependencies(self, task_name: str, resolved: set = None) -> list[str]:
        """Resolve task dependencies (topological sort)"""
        if resolved is None:
            resolved = set()
        
        task = self.get_task(task_name)
        if not task:
            return []
        
        result = []
        depends = task.get("depends", [])
        
        for dep in depends:
            if dep not in resolved:
                result.extend(self.resolve_dependencies(dep, resolved))
        
        if task_name not in resolved:
            result.append(task_name)
            resolved.add(task_name)
        
        return result

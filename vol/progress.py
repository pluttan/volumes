"""Progress bar utilities using rich"""

from typing import Optional
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn

from .output import console

# Global progress instance
_progress: Optional[Progress] = None
_main_task_id: Optional[int] = None
_sub_task_id: Optional[int] = None
_started: bool = False


def create_progress(total_steps: int, description: str = "Выполнение") -> Progress:
    """Create a progress bar (not started, rendered externally)"""
    global _progress, _main_task_id, _sub_task_id, _started
    
    _progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
        transient=True,
        auto_refresh=False,  # Will be refreshed by external Live
    )
    
    _started = True
    _main_task_id = _progress.add_task(description, total=total_steps)
    _sub_task_id = None
    
    return _progress


def create_sub_progress(total_steps: int, description: str):
    """Add a sub-task progress bar"""
    global _sub_task_id
    if _progress is None:
        return
    
    # Remove existing sub-task if any
    if _sub_task_id is not None:
        _progress.remove_task(_sub_task_id)
        
    _sub_task_id = _progress.add_task(description, total=total_steps)


def remove_sub_progress():
    """Remove sub-task progress bar"""
    global _sub_task_id
    if _progress is not None and _sub_task_id is not None:
        _progress.remove_task(_sub_task_id)
        _sub_task_id = None


def advance_progress(step: int = 1, description: Optional[str] = None):
    """Advance main progress bar by step"""
    if _progress is None or _main_task_id is None:
        return
    
    if description:
        _progress.update(_main_task_id, advance=step, description=description)
    else:
        _progress.update(_main_task_id, advance=step)


def advance_sub_progress(step: int = 1):
    """Advance sub-task progress bar by step"""
    if _progress is None or _sub_task_id is None:
        return
    _progress.update(_sub_task_id, advance=step)


def stop_progress():
    """Stop and remove progress bar"""
    global _progress, _main_task_id, _sub_task_id, _started
    
    _progress = None
    _main_task_id = None
    _sub_task_id = None
    _started = False


def get_progress() -> Optional[Progress]:
    """Get current progress instance"""
    return _progress


def is_progress_active() -> bool:
    """Check if progress bar is active"""
    return _progress is not None


def pause_progress():
    """Pause progress bar"""
    global _started
    if _progress is not None and _started:
        _progress.stop()
        _started = False


def resume_progress():
    """Resume progress bar"""
    global _started
    if _progress is not None and not _started:
        _progress.start()
        _started = True

"""Output buffer for command output display"""


class OutputBuffer:
    """Simple output buffer showing last N lines"""
    
    def __init__(self, max_lines: int = 10, max_width: int = 0, wrap_lines: bool = True):
        self.max_lines = max_lines
        self.max_width = max_width  # 0 = no limit
        self.wrap_lines = wrap_lines
        self.lines: list[str] = []
    
    def add_line(self, line: str):
        line = line.rstrip()
        
        if self.max_width > 0:
            if self.wrap_lines:
                # Wrap long lines into multiple lines
                while len(line) > self.max_width:
                    self.lines.append(line[:self.max_width])
                    line = line[self.max_width:]
                if line:
                    self.lines.append(line)
            else:
                # Truncate long lines
                if len(line) > self.max_width:
                    line = line[:self.max_width - 3] + "..."
                self.lines.append(line)
        else:
            self.lines.append(line)
        
        # Keep only last max_lines
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
    
    def line_count(self) -> int:
        """Return current number of lines in buffer"""
        return len(self.lines)
    
    def get_display(self) -> str:
        """Return display with actual lines only"""
        if not self.lines:
            return ""
        return "\n".join(self.lines)

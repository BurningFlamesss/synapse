from rich.console import Console
from rich.theme import Theme

AGENT_THEME = Theme(
    {
        "info": "blue",
        "warning": "yellow",
        "error": "red bold",
        "success": "green",
        "dim": "dim",
        "muted": "grey50",
        "border": "grey35",
        "highlight": "blue bold",
        "user": "bright_blue bold",
        "assistant": "bright_white",
        "tool": "magenta bold",
        "tool.read": "blue",
        "tool.write": "yellow",
        "tool.shell": "magenta",
        "tool.network": "blue",
        "tool.memory": "green",
        "tool.mcp": "bright_blue",
        "code": "white"
    }
)


_console: Console | None = None

def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console(theme=AGENT_THEME, highlight=False)
        
    return _console

class TUI:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or get_console()
        
    def stream_assistant_delta(self, content: str) -> None:
        self.console.print(content, end="", markup=False)
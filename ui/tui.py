from typing import Any

from rich.console import Console
from rich.theme import Theme
from rich.rule import Rule
from rich.text import Text

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
        self._assistant_stream_open = False
        self._tool_args_by_call_id: dict[str, dict[str, Any]] = {}
        
    def begin_assistant(self) -> None:
        self.console.print()
        self.console.print(Rule(Text("Assistant", style="assistant")))
        self._assistant_stream_open = True
        
    def end_assistant(self) -> None:
        if self._assistant_stream_open:
            self.console.print()
        self._assistant_stream_open = False
        
    def stream_assistant_delta(self, content: str) -> None:
        self.console.print(content, end="", markup=False)
        
    def tool_call_start(self, call_id: str, name: str, arguments: dict[str, Any]) -> None:
        self._tool_args_by_call_id[call_id] = arguments
from pathlib import Path
import re
from typing import Any

from rich.console import Console, Group
from rich.theme import Theme
from rich.rule import Rule
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from rich.live import Live
from config.config import Config
from utils.paths import display_path_rel_to_cwd
from utils.text import truncate_text
import random
import threading
import time

AGENT_THEME = Theme(
    {
        "info": "bright_cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "bright_green",
        "dim": "grey50",
        "muted": "grey62",
        "border": "grey27",
        "highlight": "bold bright_white",
        "accent": "bright_cyan",
        "user": "bright_white bold",
        "assistant": "bright_white",
        "tool": "bright_cyan bold",
        "tool.read": "bright_cyan",
        "tool.write": "bright_yellow",
        "tool.shell": "bright_magenta",
        "tool.network": "bright_blue",
        "tool.memory": "bright_green",
        "tool.mcp": "bright_cyan",
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
    def __init__(self, config: Config, console: Console | None = None) -> None:
        self.console = console or get_console()
        self.config = config
        self._assistant_stream_open = False
        self._assistant_buffer: list[str] = []
        self._tool_args_by_call_id: dict[str, dict[str, Any]] = {}
        self.cwd = self.config.cwd
        self.max_block_tokens = 2500
        self._pet_profiles = [
            {
                "name": "Sunsun",
                "frames": ["(=^.^=)", "(=^o^=)", "(=^.^=)"]
            },
            {
                "name": "Ramama",
                "frames": ["(=^.^=)", "(=^_^=)", "(=^.^=)"]
            },
            {
                "name": "Sursur",
                "frames": ["(=^.^=)", "(=^x^=)", "(=^.^=)"]
            },
        ]
        self._loading_phrases = [
            "Thinking", "Planning", "Working"
        ]
        self._active_pet = random.choice(self._pet_profiles)
        self._pet_frame_index = 0
        self._loading_live: Live | None = None
        self._loading_thread: threading.Thread | None = None
        self._loading_stop = threading.Event()
        self._loading_phrase_index = 0
        
    def begin_assistant(self) -> None:
        self.console.print()
        self.console.print(Rule(Text("Assistant", style="assistant"), style="border", characters="-"))
        self._assistant_stream_open = True
        self._assistant_buffer = []
        
    def end_assistant(self) -> None:
        if self._assistant_stream_open:
            content = "".join(self._assistant_buffer).strip()
            if content:
                panel = Panel(Markdown(content, code_theme="monokai"), border_style="border", box=box.ROUNDED, padding=(1,2))
                self.console.print(panel)
            else:
                self.console.print()
        self._assistant_stream_open = False
        
    def stream_assistant_delta(self, content: str) -> None:
        if content:
            self._assistant_buffer.append(content)
            # self.console.print(content, end="", markup=False)
            
    def _current_pet_frame(self) -> str:
        frames = self._active_pet["frames"]
        return frames[self._pet_frame_index % len(frames)]
    
    def _pet_status_text(self, status: str) -> Text:
        name = self._active_pet["name"]
        frame = self._current_pet_frame()
        return Text(f"{status}  {frame} {name}", style="muted")
    
    def start_loading(self) -> None:
        if self._loading_live: 
            return

        self._active_pet = random.choice(self._pet_profiles)
        self._pet_frame_index = 0
        self._loading_phrase_index = 0
        self._loading_stop.clear()
        
        self._loading_live = Live(
            Panel(
                self._loading_text(),
                border_style="border",
                box=box.ROUNDED,
                padding=(0, 2)
            ),
            console=self.console,
            refresh_per_second=6,
            transient=True
        )
        self._loading_live.start()
        
        def _run() -> None:
            pass
        
    def stop_loading(self) -> None:
        pass
    
    def _loading_text(self) -> Text:
        phrase = self._loading_phrases[self._loading_phrase_index % len(self._loading_phrases)]
        frame = self._current_pet_frame()
        name = self._active_pet["name"]
        return Text(f"{phrase}...  {frame} {name}", style="muted")
        
    def _ordered_args(self, tool_name: str, args: dict[str, Any]) -> list[tuple]:
        _PREFERRED_ORDER = {
            "read_file": ["path", "offset", "limit"],
        }
        
        preferred = _PREFERRED_ORDER.get(tool_name, [])
        ordered: list[tuple[str, Any]] = []
        seen = set()
        
        for key in preferred:
            if key in args:
                ordered.append((key, args[key]))
                seen.add(key)
                
        remaining_keys = set(args.keys() - seen)
        ordered.extend((key, args[key]) for key in remaining_keys)
        
        return ordered
        
    def _render_args_tab(self, tool_name: str, args: dict[str, Any]) -> Table:
        table = Table.grid(padding=(0,1))
        table.add_column(style="muted", justify="right", no_wrap=True)
        table.add_column(style="code", overflow="fold")
        
        for key, value in self._ordered_args(tool_name, args):
            table.add_row(key, value)
            
        return table
        
    def tool_call_start(self, call_id: str, name: str, tool_kind: str | None, arguments: dict[str, Any]) -> None:
        self._tool_args_by_call_id[call_id] = arguments
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"
        
        title = Text.assemble(
            ("⏺ ", "muted"),
            (name, "tool"),
            ("  ", "muted"),
            (f"#{call_id[:8]}", "muted")
        )
        
        display_args = dict(arguments)
        for key in ("path", "cwd"):
            val = display_args.get(key)
            if isinstance(val, str) and self.cwd:
                display_args[key] = str(display_path_rel_to_cwd(val, self.cwd))
        
        panel = Panel(
            self._render_args_tab(name, display_args) if display_args else Text("(no args)", style="muted"),
            title=title,
            title_align="left",
            subtitle=Text("running", style="muted"),
            subtitle_align="right",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1,2)
        )
        
        self.console.print()
        self.console.print(panel)
        
    def _extract_read_file_code(self, text: str) -> tuple[int, str] | None:
        body = text
        header_match = re.match(r"^Showing lines (\d+)-(\d+) of (\d+)\n\n", text)
        if header_match:
            body = text[header_match.end() :]
            
        code_lines: list[str] = []
        start_lines: int | None = None
        end_lines: int | None = None
        
        for line in body.splitlines():
            m = re.match(r"^\s*(\d+)\|(.*)$", line)
            if not m:
                return None
            line_no = int(m.group(1))
            if start_lines is None:
                start_lines = line_no
            code_lines.append(m.group(2))
            
        if start_lines is None:
            return None
        
        return start_lines, "\n".join(code_lines)
    
    def _guess_language(self, path: str | None) -> str:
        if not path:
            return "text"
        suffix = Path(path).suffix.lower()
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".json": "json",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".kt": "kotlin",
            ".swift": "swift",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".css": "css",
            ".html": "html",
            ".xml": "xml",
            ".sql": "sql",
        }.get(suffix, "text")
        
    def print_welcome(self, title: str, lines: list[str]) -> None:
        body = "\n".join(lines)
        self.console.print()
        self.console.print(
            Panel(
                Text(body, style="code"),
                title=Text(title, style="highlight"),
                title_align="left",
                border_style="border",
                box=box.ROUNDED,
                padding=(1,2)
            )
        )
        
    def tool_call_complete(self, call_id: str, name: str, tool_kind: str | None, success: str, output: str, error: str | None, metadata: dict[str, Any] | None, truncated: bool) -> None:
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"
        status_icon = "✓" if success else "X"
        status_style = "success" if success else "error"
        
        title = Text.assemble(
            (f"{status_icon} ", status_style),
            (name, "tool"),
            ("  ", "muted"),
            (f"#{call_id[:8]}", "muted")
        )
        primary_path = None
        blocks = []
        if isinstance(metadata, dict) and isinstance(metadata.get("path"), str):
            primary_path = metadata.get("path")
        
        if name == "read_file" and success:
            if primary_path:
                start_line, code = self._extract_read_file_code(output)
                shown_start = metadata.get("shown_start")
                shown_end = metadata.get("shown_end")
                total_lines = metadata.get("total_lines")
                pl = self._guess_language(primary_path)
                
                header_parts = [display_path_rel_to_cwd(primary_path, self.cwd)]
                header_parts.append(" ⏺ ")
                if shown_start and shown_end and total_lines:
                    header_parts.append(f"lines {shown_start}-{shown_end} of {total_lines}")
                    
                header = "".join(header_parts)
                blocks.append(Text(header, style="muted"))
                blocks.append(Text("", style="muted"))
                blocks.append(Syntax(
                    code,
                    pl,
                    theme="monokai",
                    line_numbers=True,
                    start_line=start_line,
                    word_wrap=False
                ))
            else:
                output_display = truncate_text(output, "", 240)
                blocks.append(
                    Syntax(
                        output_display,
                        "text",
                        line_numbers=True,
                        theme="monokai",
                        word_wrap=False
                    )
                )
                
        if truncated:
            blocks.append(Text("Note: The code was truncated", style="warning"))
        
        panel = Panel(
            Group(*blocks),
            title=title,
            title_align="left",
            subtitle=Text("done" if success else "failed", style=status_style),
            subtitle_align="right",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1,2)
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
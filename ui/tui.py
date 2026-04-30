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
from tools.base import ToolConfirmation
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
        self._assistant_stream_open = False
        self._assistant_buffer: list[str] = []
        self._tool_args_by_call_id: dict[str, dict[str, Any]] = {}
        self.config = config
        self.cwd = self.config.cwd
        self._max_block_tokens = 2500
        self._pet_profiles = [
            {
                "name": "Sursur",
                "frames": ["(=^.^=)", "(=^o^=)", "(=^.^=)"],
            },
            {
                "name": "Ramama",
                "frames": ["(=^.^=)", "(=^_^=)", "(=^.^=)"],
            },
            {
                "name": "Sunsun",
                "frames": ["(=^.^=)", "(=^x^=)", "(=^.^=)"],
            },
        ]
        self._loading_phrases = [
            "Thinking",
            "Planning",
            "Scanning",
        ]
        self._active_pet = random.choice(self._pet_profiles)
        self._pet_frame_index = 0
        self._loading_live: Live | None = None
        self._loading_thread: threading.Thread | None = None
        self._loading_stop = threading.Event()
        self._loading_phrase_index = 0
        
    def begin_assistant(self) -> None:
        self.console.print()
        self.console.print(
            Rule(
                Text("Assistant", style="assistant"),
                style="border",
                characters="-",
            )
        )
        self._assistant_stream_open = True
        self._assistant_buffer = []

    def end_assistant(self) -> None:
        if self._assistant_stream_open:
            content = "".join(self._assistant_buffer).strip()
            if content:
                panel = Panel(
                    Markdown(content, code_theme="monokai"),
                    border_style="border",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
                self.console.print(panel)
            else:
                self.console.print()
        self._assistant_stream_open = False

    def stream_assistant_delta(self, content: str) -> None:
        if content:
            self._assistant_buffer.append(content)

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
                padding=(0, 2),
            ),
            console=self.console,
            refresh_per_second=6,
            transient=True,
        )
        self._loading_live.start()

        def _run() -> None:
            tick = 0
            while not self._loading_stop.is_set():
                time.sleep(0.25)
                tick += 1
                self._pet_frame_index += 1
                if tick % 4 == 0:
                    self._loading_phrase_index += 1
                if self._loading_live:
                    self._loading_live.update(
                        Panel(
                            self._loading_text(),
                            border_style="border",
                            box=box.ROUNDED,
                            padding=(0, 2),
                        )
                    )

        self._loading_thread = threading.Thread(target=_run, daemon=True)
        self._loading_thread.start()

    def stop_loading(self) -> None:
        if not self._loading_live:
            return

        self._loading_stop.set()
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_thread.join(timeout=0.5)
        self._loading_live.stop()
        self._loading_live = None
        self._loading_thread = None

    def _loading_text(self) -> Text:
        phrase = self._loading_phrases[
            self._loading_phrase_index % len(self._loading_phrases)
        ]
        frame = self._current_pet_frame()
        name = self._active_pet["name"]
        return Text(f"{phrase}...  {frame} {name}", style="muted")
        
    def _ordered_args(self, tool_name: str, args: dict[str, Any]) -> list[tuple]:
        _PREFERRED_ORDER = {
            "read_file": ["path", "offset", "limit"],
            "write_file": ["path", "create_directories", "content"],
            "edit": ["path", "replace_all", "old_string", "new_string"],
            "shell": ["command", "timeout", "cwd"],
            "list_dir": ["path", "include_hidden"],
            "grep": ["path", "case_insensitive", "pattern"],
            "glob": ["path", "pattern"],
            "todos": ["id", "action", "content"],
            "memory": ["action", "key", "value"],
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
        
    def _render_args_table(self, tool_name: str, args: dict[str, Any]) -> Table:
        table = Table.grid(padding=(0, 1))
        table.add_column(style="muted", justify="right", no_wrap=True)
        table.add_column(style="code", overflow="fold")

        for key, value in self._ordered_args(tool_name, args):
            if isinstance(value, str):
                if key in {"content", "old_string", "new_string"}:
                    line_count = len(value.splitlines()) or 0
                    byte_count = len(value.encode("utf-8", errors="replace"))
                    value = f"<{line_count} lines • {byte_count} bytes>"

            if not isinstance(value, str):
                value = str(value)

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
            self._render_args_table(name, display_args) if display_args else Text("(no args)", style="muted"),
            title=title,
            title_align="left",
            subtitle=self._pet_status_text("running"),
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
        header = Text.assemble(
            ("Synapse", "highlight"),
            ("   ", "muted"),
            ("ready", "accent"),
        )
        self.console.print()
        self.console.print(
            Panel(
                Text(body, style="code"),
                title=header,
                title_align="left",
                border_style="border",
                box=box.ROUNDED,
                padding=(1,2)
            )
        )
        
    def tool_call_complete(
        self,
        call_id: str,
        name: str,
        tool_kind: str | None,
        success: bool,
        output: str,
        error: str | None,
        metadata: dict[str, Any] | None,
        diff: str | None,
        truncated: bool,
        exit_code: int | None,
    ) -> None:
        border_style = f"tool.{tool_kind}" if tool_kind else "tool"
        status_icon = "✓" if success else "✗"
        status_style = "success" if success else "error"

        title = Text.assemble(
            (f"{status_icon} ", status_style),
            (name, "tool"),
            ("  ", "muted"),
            (f"#{call_id[:8]}", "muted"),
        )

        args = self._tool_args_by_call_id.get(call_id, {})

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
                header_parts.append(" • ")

                if shown_start and shown_end and total_lines:
                    header_parts.append(
                        f"lines {shown_start}-{shown_end} of {total_lines}"
                    )

                header = "".join(header_parts)
                blocks.append(Text(header, style="muted"))
                blocks.append(
                    Syntax(
                        code,
                        pl,
                        theme="monokai",
                        line_numbers=True,
                        start_line=start_line,
                        word_wrap=False,
                    )
                )
            else:
                output_display = truncate_text(
                    output,
                    "",
                    self._max_block_tokens,
                )
                blocks.append(
                    Syntax(
                        output_display,
                        "text",
                        theme="monokai",
                        word_wrap=False,
                    )
                )
        elif name in {"write_file", "edit"} and success and diff:
            output_line = output.strip() if output.strip() else "Completed"
            blocks.append(Text(output_line, style="muted"))
            diff_text = diff
            diff_display = truncate_text(
                diff_text,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    diff_display,
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "shell" and success:
            command = args.get("command")
            if isinstance(command, str) and command.strip():
                blocks.append(Text(f"$ {command.strip()}", style="muted"))

            if exit_code is not None:
                blocks.append(Text(f"exit_code={exit_code}", style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "list_dir" and success:
            entries = metadata.get("entries")
            path = metadata.get("path")
            summary = []
            if isinstance(path, str):
                summary.append(path)

            if isinstance(entries, int):
                summary.append(f"{entries} entries")

            if summary:
                blocks.append(Text(" • ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "grep" and success:
            matches = metadata.get("matches")
            files_searched = metadata.get("files_searched")
            summary = []
            if isinstance(matches, int):
                summary.append(f"{matches} matches")
            if isinstance(files_searched, int):
                summary.append(f"searched {files_searched} files")

            if summary:
                blocks.append(Text(" • ".join(summary), style="muted"))

            output_display = truncate_text(
                output, self.config.model_name, self._max_block_tokens
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "glob" and success:
            matches = metadata.get("matches")
            if isinstance(matches, int):
                blocks.append(Text(f"{matches} matches", style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "web_search" and success:
            results = metadata.get("results")
            query = args.get("query")
            summary = []
            if isinstance(query, str):
                summary.append(query)
            if isinstance(results, int):
                summary.append(f"{results} results")

            if summary:
                blocks.append(Text(" • ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "web_fetch" and success:
            status_code = metadata.get("status_code")
            content_length = metadata.get("content_length")
            url = args.get("url")
            summary = []
            if isinstance(status_code, int):
                summary.append(str(status_code))
            if isinstance(content_length, int):
                summary.append(f"{content_length} bytes")
            if isinstance(url, str):
                summary.append(url)

            if summary:
                blocks.append(Text(" • ".join(summary), style="muted"))

            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "todos" and success:
            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        elif name == "memory" and success:
            action = args.get("action")
            key = args.get("key")
            found = metadata.get("found")
            summary = []
            if isinstance(action, str) and action:
                summary.append(action)
            if isinstance(key, str) and key:
                summary.append(key)
            if isinstance(found, bool):
                summary.append("found" if found else "missing")

            if summary:
                blocks.append(Text(" • ".join(summary), style="muted"))
            output_display = truncate_text(
                output,
                self.config.model_name,
                self._max_block_tokens,
            )
            blocks.append(
                Syntax(
                    output_display,
                    "text",
                    theme="monokai",
                    word_wrap=True,
                )
            )
        else:
            if error and not success:
                blocks.append(Text(error, style="error"))

            output_display = truncate_text(
                output, self.config.model_name, self._max_block_tokens
            )
            if output_display.strip():
                blocks.append(
                    Syntax(
                        output_display,
                        "text",
                        theme="monokai",
                        word_wrap=True,
                    )
                )
            else:
                blocks.append(Text("(no output)", style="muted"))

        if truncated:
            blocks.append(Text("note: tool output was truncated", style="warning"))

        panel = Panel(
            Group(
                *blocks,
            ),
            title=title,
            title_align="left",
            subtitle=Text(
                f"{'done' if success else 'failed'}  {self._current_pet_frame()} {self._active_pet['name']}",
                style=status_style,
            ),
            subtitle_align="right",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()
        
        
        
    def handle_confirmation(self, confirmation: ToolConfirmation) -> bool:
        was_loading = self._loading_live is not None
        if was_loading:
            self.stop_loading()

        output = [
            Text(confirmation.tool_name, style="tool"),
            Text(confirmation.description, style="code"),
        ]

        if confirmation.command:
            output.append(Text(f"$ {confirmation.command}", style="warning"))

        if confirmation.diff:
            diff_text = confirmation.diff.to_diff()
            output.append(
                Syntax(
                    diff_text,
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                )
            )

        self.console.print()
        self.console.print(
            Panel(
                Group(*output),
                title=Text("Approval required", style="warning"),
                title_align="left",
                border_style="warning",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        self.console.print(
            Text("Type 'y' or 'yes' to approve, 'n' or 'no' to reject.", style="muted")
        )

        try:
            while True:
                response = self.console.input("\n[warning]Approve? [y/n][/warning] ").strip().lower()
                if response in {"y", "yes"}:
                    return True
                if response in {"n", "no"}:
                    return False
                self.console.print("[warning]Please enter y/yes or n/no.[/warning]")
        finally:
            if was_loading:
                self.start_loading()
                
    def show_help(self) -> None:
        help_text = """
## Commands

- `/help` - Show this help
- `/exit` or `/quit` - Exit the agent
- `/clear` - Clear conversation history
- `/undo` - Undo last edit (multi-step)
- `/config` - Show current configuration
- `/model <name>` - Change the model
- `/approval <mode>` - Change approval mode
- `/stats` - Show session statistics
- `/tools` - List available tools
- `/mcp` - Show MCP server status
- `/save` - Save current session
- `/checkpoint [name]` - Create a checkpoint
- `/checkpoints` - List available checkpoints
- `/restore <checkpoint_id>` - Restore a checkpoint
- `/sessions` - List saved sessions
- `/resume <session_id>` - Resume a saved session

## Tips

- Just type your message to chat with the agent
- The agent can read, write, and execute code
- Some operations require approval (can be configured)
"""
        self.console.print(Markdown(help_text))
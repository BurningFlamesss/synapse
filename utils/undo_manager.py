from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.base import FileDiff
from utils.paths import ensure_parent_directory


@dataclass
class UndoEntry:
    diff: FileDiff
    tool_name: str
    metadata: dict[str, Any] | None = None


class UndoManager:
    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd
        self._stack: list[UndoEntry] = []
        self._is_undoing = False

    def record(self, diff: FileDiff, tool_name: str, metadata: dict[str, Any] | None = None) -> None:
        if self._is_undoing:
            return

        entry = UndoEntry(diff=diff, tool_name=tool_name, metadata=metadata)
        self._stack.append(entry)

    def can_undo(self) -> bool:
        return bool(self._stack)

    def undo_last(self) -> tuple[bool, str]:
        if not self._stack:
            return False, "No undo history available."

        entry = self._stack.pop()
        diff = entry.diff
        path = diff.path

        try:
            self._is_undoing = True
            if diff.is_new_file:
                if path.exists():
                    path.unlink()
                return True, f"Removed new file: {path}"

            ensure_parent_directory(path)
            path.write_text(diff.old_content, encoding="utf-8")
            return True, f"Reverted file: {path}"
        except Exception as e:
            return False, f"Failed to undo change: {e}"
        finally:
            self._is_undoing = False
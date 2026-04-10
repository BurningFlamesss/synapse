from tools.base import Tool
from tools.built.read_file import ReadFileTool

__all__ = [
    'ReadFileTool'
]

def get_all_builtin_tools() -> list[Tool]:
    return [ReadFileTool]
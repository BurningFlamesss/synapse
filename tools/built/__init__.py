from tools.built.edit_file import EditTool
from tools.built.list_dir import ListDirTool
from tools.built.memory import MemoryTool
from tools.built.read_file import ReadFileTool
from tools.built.shell import ShellTool
from tools.built.todo import TodosTool
from tools.built.write_file import WriteFileTool

__all__ = [
    'ReadFileTool', 'WriteFileTool', 'EditTool', 'ShellTool', 'ListDirTool', 'TodosTool', 'MemoryTool'
]

def get_all_builtin_tools() -> list[type]:
    return [ReadFileTool, WriteFileTool, EditTool, ShellTool, ListDirTool, TodosTool, MemoryTool]
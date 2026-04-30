from tools.built.edit_file import EditTool
from tools.built.glob import GlobTool
from tools.built.grep import GrepTool
from tools.built.list_dir import ListDirTool
from tools.built.memory import MemoryTool
from tools.built.read_file import ReadFileTool
from tools.built.shell import ShellTool
from tools.built.todo import TodosTool
from tools.built.web_fetch import WebFetchTool
from tools.built.web_search import WebSearchTool
from tools.built.write_file import WriteFileTool

__all__ = [
    'ReadFileTool', 'WriteFileTool', 'EditTool', 'ShellTool', 'ListDirTool', 'TodosTool', 'MemoryTool'
]

def get_all_builtin_tools() -> list[type]:
    return [ReadFileTool, WriteFileTool, EditTool, ShellTool, ListDirTool, GrepTool, GlobTool, WebSearchTool, WebFetchTool, TodosTool, MemoryTool]
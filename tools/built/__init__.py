from tools.built.edit_file import EditTool
from tools.built.read_file import ReadFileTool
from tools.built.write_file import WriteFileTool

__all__ = [
    'ReadFileTool', 'WriteFileTool', 'EditTool'
]

def get_all_builtin_tools() -> list[type]:
    return [ReadFileTool, WriteFileTool, EditTool]
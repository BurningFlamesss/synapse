from tools.built.read_file import ReadFileTool
from tools.built.write_file import WriteFileTool

__all__ = [
    'ReadFileTool', 'WriteFileTool'
]

def get_all_builtin_tools() -> list[type]:
    return [ReadFileTool, WriteFileTool]
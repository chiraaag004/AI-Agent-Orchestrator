import os
import importlib.util
import inspect
from langchain.tools import BaseTool

def load_tools_from_directory(directory: str) -> dict:
    """
    Dynamically loads all LangChain tools from a given directory.

    This function scans all .py files in the specified directory,
    imports them as modules, and inspects them to find any objects
    that are instances of LangChain's BaseTool (which the @tool decorator creates).

    Args:
        directory (str): The relative path to the directory containing tool files.

    Returns:
        dict: A dictionary mapping tool names to their corresponding tool objects.
    """
    tool_map = {}
    tools_dir = os.path.abspath(directory)

    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("__init__"):
            module_name = f"tools.{filename[:-3]}"
            file_path = os.path.join(tools_dir, filename)

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if isinstance(obj, BaseTool):
                        tool_map[obj.name] = obj

    return tool_map
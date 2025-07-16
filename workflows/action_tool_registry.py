from utils.tool_loader import load_tools_from_directory

# The TOOL_MAP is now created dynamically by scanning the 'tools' directory.
TOOL_MAP = load_tools_from_directory("tools")
from langchain.tools import tool

@tool
def emergency_help_tool(query: str) -> str:
    """Provide emergency support contact info or assistance."""
    return "🚨 Please call our emergency hotline at 1800-999-HELP or go to the nearest help desk immediately."

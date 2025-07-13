from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()

# Set project config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-pro")

# API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# Router settings
CONFIDENCE_THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", 70))

# New agent architecture: Define agents and their specific tools.
# The keys are the agent names the router will use.
# The values are the names of the tools for that agent. A value of `None`
# means the agent has access to all available tools.
AGENT_TOOL_MAPPING = {
    "flight_booking_manager": [
        "book_flight_tool",
        "cancel_booking_tool"
    ],
    "support_agent": [
        "faq_tool" # Handles general FAQs and policy questions
    ],
    "flight_information": [
        "flight_status_tool"
    ],
    "emergency_services": [
        "emergency_help_tool"
    ],
    "general": None # Fallback agent with access to all tools
}

# The router will now choose from these high-level agent capabilities.
ROUTER_INTENTS = list(AGENT_TOOL_MAPPING.keys())

# Agent Memory settings
CONVERSATION_WINDOW_SIZE = int(os.getenv("CONVERSATION_WINDOW_SIZE", 6))

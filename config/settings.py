import os

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
        "book_flight_tool", # Matches book_flight.py
        "cancel_booking_tool" # Matches cancel_booking.py
    ],
    "support_agent": [
        "faq_tool" # Matches faq_tool.py
    ],
    "flight_information": [
        "get_flight_status" # Matches flight_status_checker.py
    ],
    "emergency_services": [
        "emergency_help_tool" # Matches emergency_help.py
    ],
    "itinerary_checker": [
        "check_flight_itinerary" # Matches itinerary_checker.py
    ],
    "general": None # Fallback agent with access to all tools
}

# The router will now choose from these high-level agent capabilities.
ROUTER_INTENTS = list(AGENT_TOOL_MAPPING.keys())

# Agent Memory settings
CONVERSATION_WINDOW_SIZE = int(os.getenv("CONVERSATION_WINDOW_SIZE", 6))

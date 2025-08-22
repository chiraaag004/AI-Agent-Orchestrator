import os

# Set project config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-pro")

# API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# Router settings
confidence_str = os.getenv("CONFIDENCE_THRESHOLD", "70")
CONFIDENCE_THRESHOLD = int(confidence_str.split('#')[0].strip())

silence_threshold_str = os.getenv("SILENCE_THRESHOLD_S", "0.7")
# Strip inline comments and whitespace before converting to handle malformed .env files
SILENCE_THRESHOLD_S = float(silence_threshold_str.split('#')[0].strip())

# Voice Service settings
# Whisper model for Speech-to-Text (e.g., tiny.en, base.en, small.en)
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "base.en")
WHISPER_DOWNLOAD_ROOT = os.getenv("WHISPER_DOWNLOAD_ROOT", "models/stt")
PIPER_VOICE_MODEL_PATH = os.getenv("PIPER_VOICE_MODEL_PATH", "models/tts/en_US-lessac-medium.onnx")

# New agent architecture: Define agents and their specific tools.
# The keys are the agent names the router will use.
# The values are the names of the tools for that agent. A value of `None`
# means the agent has access to all available tools.
AGENT_TOOL_MAPPING = {
    "support_agent": [
        "faq_tool"
    ],
    "emergency_services": [
        "emergency_help_tool"
    ],
    "hotel_services": [
        "book_room_tool",
        "room_service_tool",
        "hotel_faq_tool",
        "get_hotel_info_tool",
        "get_room_details_tool",
        "check_availability_tool",
        "group_booking_tool",
        "get_media_tool",
        "upsell_recommendation_tool",
        "search_knowledge_base",
    ],
    "attractions_agent": [
        "find_nearby_attractions_tool",
        "provide_local_recommendations_tool"
    ],
    "transportation_agent": [
        "local_transport_tool",
        "book_local_transport_tool"
    ],
    "weather_checker": [
        "get_weather_forecast"
    ],
    "promotions_agent": [
        "festival_promotion_tool"
    ],
    "general": None
}

# The router will now choose from these high-level agent capabilities.
ROUTER_INTENTS = list(AGENT_TOOL_MAPPING.keys())

# Agent Memory settings
conversation_window_str = os.getenv("CONVERSATION_WINDOW_SIZE", "6")
CONVERSATION_WINDOW_SIZE = int(conversation_window_str.split('#')[0].strip())

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
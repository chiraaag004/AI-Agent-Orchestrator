# d:\Work\ai_hackathon\workflows\language_helpers.py
from config.llm_loader import load_llm
from utils.prompt_loader import load_prompt_from_file

# Use the same shared LLM instance
SHARED_LLM = load_llm()

# --- Prompts for Language Tasks ---
DETECTION_PROMPT = load_prompt_from_file("config/prompts/language_detection_prompt.txt")
TRANSLATION_PROMPT = load_prompt_from_file("config/prompts/translation_prompt.txt")

# --- Chains for Language Tasks ---

detection_chain = DETECTION_PROMPT | SHARED_LLM
translation_chain = TRANSLATION_PROMPT | SHARED_LLM

# --- Helper Functions ---

def detect_language(text: str) -> str:
    """Detects the language of a given text and returns the ISO 639-1 code."""
    if not text.strip():
        return "en" # Default to English for empty strings
    response = detection_chain.invoke({"text": text})
    return response.content.strip().lower()

def translate_text(text: str, target_language: str, original_query: str = "") -> str:
    """Translates text to the target language, handling transliteration."""
    if not text.strip():
        return text
    response = translation_chain.invoke({"text": text, "target_language": target_language, "original_query": original_query})
    return response.content.strip()
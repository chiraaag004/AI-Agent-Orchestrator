from config.settings import LLM_PROVIDER, MODEL_NAME, GOOGLE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def load_llm():
    """
    Loads and returns the specified LLM provider and model based on environment settings.

    Raises:
        ValueError: If the required API key for the selected provider is not found.
        ValueError: If the LLM_PROVIDER is not supported.

    Returns:
        An instance of a LangChain chat model.
    """
    provider = LLM_PROVIDER.lower()

    if provider == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment. Please set it in your .env file.")
        # The new create_react_agent handles system messages correctly, so convert_system_message_to_human is no longer needed.
        return ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=GOOGLE_API_KEY)
    elif provider == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment. Please set it in your .env file.")
        return ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY)
    elif provider == "claude":
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment. Please set it in your .env file.")
        return ChatAnthropic(model=MODEL_NAME, api_key=ANTHROPIC_API_KEY)
    else:
        raise ValueError(f"Unsupported LLM provider specified in .env: '{LLM_PROVIDER}'")
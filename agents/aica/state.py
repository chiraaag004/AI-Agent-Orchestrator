# d:\Work\ai_hackathon\agents\aica\state.py
from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage
from langchain.memory import VectorStoreRetrieverMemory

class AgentState(TypedDict):
    """
    Represents the state of the AI Call Agent.
    """
    original_query: str                     # The original user query, untouched.
    detected_language: str                  # The language code detected from the original query (e.g., 'es', 'fr', 'en').
    messages: List[BaseMessage]             # The list of messages that forms the conversation.
    intents: List[str]                      # List of intents identified by the router.
    confidence: int                         # Confidence score from the router.
    processed_intents: List[str]            # Intents that have been processed by an agent.
    last_completed_intent: Optional[str]    # The last intent that was completed.
    output: str                             # The raw output from the last agent run.
    aggregated_output: str                  # The aggregated output from all agent runs, which is synthesized for the final response.
    memory: Optional[VectorStoreRetrieverMemory] # Session-specific long-term memory object.
    current_time: str                       # The current time in ISO format.
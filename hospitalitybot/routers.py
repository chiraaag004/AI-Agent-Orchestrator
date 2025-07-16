# hospitalitybot/routers.py
from .state import AgentState

def initial_router(state: AgentState) -> str:
    """
    This router runs once after the llm_router to kick off the first task.
    It routes to the first intent in the list.
    """
    intents = state.get("intents", [])
    if intents:
        return intents[0]
    return "general" # Fallback

def continuation_router(state: AgentState) -> str:
    """
    This router runs after the aggregator to decide what to do next.
    - If there are more intents to process, it routes to the next agent.
    - If all intents are processed, it routes to the final output node.
    """
    processed = set(state.get("processed_intents", []))
    all_intents = state.get("intents", [])

    # Find the next intent in the list that hasn't been processed yet.
    # This is more robust than comparing lengths and handles repeated intents.
    for intent in all_intents:
        if intent not in processed:
            return intent

    # If all intents in the list have been processed, we are done.
    return "FINISH"
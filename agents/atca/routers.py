# agents/atca/routers.py
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
    processed = state.get("processed_intents", [])
    all_intents = state.get("intents", [])
    if len(processed) == len(all_intents):
        return "FINISH" # All tasks are done
    else:
        # Find the next unprocessed intent
        next_intent = [i for i in all_intents if i not in processed][0]
        return next_intent
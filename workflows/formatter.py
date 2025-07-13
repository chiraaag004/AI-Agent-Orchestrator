# workflows/formatter.py
from agents.atca.state import AgentState
from langchain_core.messages import AIMessage

def format_output(state: AgentState) -> dict:
    """
    Takes the final aggregated output and formats it into an AIMessage,
    adding it to the conversation history. This makes the AI's response
    part of the state for the next turn in a conversation.
    """
    # Get the final response synthesized by the summarizer
    final_response = state.get("aggregated_output", "I'm sorry, I don't have a response for you.")
    
    # Create the AIMessage and return it to be added to the state.
    # The `operator.add` on the `messages` field in AgentState handles appending.
    return {"messages": [AIMessage(content=final_response)]}
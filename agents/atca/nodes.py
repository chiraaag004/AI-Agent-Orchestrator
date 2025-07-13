# agents/atca/nodes.py
from .state import AgentState
from workflows.base_agent import ReActAgent
from workflows.action_tool_registry import TOOL_MAP
from config.llm_loader import load_llm
from config.settings import CONVERSATION_WINDOW_SIZE
from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage, AIMessage
from utils.prompt_loader import load_prompt_from_file

# Create a single, shared LLM instance for all nodes in this file.
SHARED_LLM = load_llm()
BASE_PROMPT = load_prompt_from_file("config/prompts/base_prompt.txt").template
FOCUSED_TASK_PROMPT = load_prompt_from_file("config/prompts/focused_task_prompt.txt")
SUMMARIZER_PROMPT = load_prompt_from_file("config/prompts/summarizer_prompt.txt")

def aggregator_node(state: AgentState) -> AgentState:
    """
    Aggregates the output from the last agent run into the final response.
    """
    intent_just_processed = state.get("last_completed_intent")
    if not intent_just_processed:
        return {}

    last_output = state.get("output", "")
    intent_title = intent_just_processed.replace("_", " ").title()
    current_aggregated = state.get("aggregated_output", "")
    new_output_part = f"Regarding {intent_title}:\n{last_output}"

    # Return only the fields this node has updated.
    return {
        "aggregated_output": f"{current_aggregated}\n\n{new_output_part}".strip(),
        "processed_intents": state.get("processed_intents", []) + [intent_just_processed],
    }

def create_agent_runner(agent_name: str, tool_names: list[str] = None):
    """Creates a graph node that runs a specialized ReActAgent."""
    def agent_runner(state: AgentState) -> AgentState:
        # 1. Get the recent conversation history from the state.
        # History sanitization is now handled inside the ReActAgent class.
        clean_history = state["messages"][-CONVERSATION_WINDOW_SIZE:]

        # 2. Prepare the tools and prompt for the agent.
        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in clean_history])
        
        # `tool_names` being `None` means use all tools. An empty list means use no tools.
        if tool_names is not None:
            # If a list of tool names is provided (even an empty one), collect them.
            tools_for_agent = {name: TOOL_MAP[name] for name in tool_names if name in TOOL_MAP}
        else:
            # Default to all tools if none are specified (e.g., for the 'general' agent).
            tools_for_agent = TOOL_MAP

        agent_instance = ReActAgent(tools_for_agent)

        task_description = "handle a general user request that did not fit a specific category" if agent_name == "general" else agent_name.replace("_", " ")

        focused_prompt_str = FOCUSED_TASK_PROMPT.format(
            intent_name=task_description,
            conversation_history=history_str
        )

        messages_for_agent = [
            SystemMessage(content=f"{BASE_PROMPT}\n\n{focused_prompt_str}")
        ] + clean_history

        agent_sub_state = {"messages": messages_for_agent}
        result_state = agent_instance(agent_sub_state)

        # Return only the new information this node generated.
        # The graph framework will merge it into the main state.
        return {
            "output": result_state.get('output', 'No output from agent.'),
            "last_completed_intent": agent_name,
        }
    return agent_runner

def summarizer_node(state: AgentState) -> AgentState:
    """
    Synthesizes the aggregated output into a final response.
    """
    aggregated_response = state.get("aggregated_output", "")
    # Use the original, untranslated query for the summarizer. This ensures the
    # final response is framed in the context of the user's exact words.
    user_query = state.get("original_query", state['messages'][-1].content)

    summarization_prompt_str = SUMMARIZER_PROMPT.format(
        user_query=user_query,
        aggregated_response=aggregated_response
    )

    final_response = SHARED_LLM.invoke(summarization_prompt_str).content
    # This node's only job is to update the final aggregated_output.
    return {"aggregated_output": final_response}
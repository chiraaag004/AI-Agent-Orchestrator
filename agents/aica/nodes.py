# agents/aica/nodes.py
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

    aggregated_output = f"{current_aggregated}\n\n{new_output_part}".strip()

    # Return updated fields. `messages` will be passed through automatically.
    return {
        "aggregated_output": aggregated_output,
        "processed_intents": state.get("processed_intents", []) + [intent_just_processed],
    }

def create_agent_runner(agent_name: str, tool_names: list[str] = None):
    """Creates a graph node that runs a specialized ReActAgent."""
    def agent_runner(state: AgentState) -> AgentState:
        # 1. Get conversation history and memory from the state.
        clean_history = state["messages"][-CONVERSATION_WINDOW_SIZE:]
    
        # Ensure last message is HumanMessage
        if not isinstance(clean_history[-1], HumanMessage):
            # This block should not be hit if state is managed correctly, but as a safeguard,
            # we ensure it doesn't modify messages and returns the current agent's name.
            return {
                "output": "No new user input to respond to.",
                "last_completed_intent": agent_name,
            }

        memory = state.get("memory")
        retrieved_memory_str = ""

        # 2. Load relevant long-term memories if the memory object exists and is valid.
        if memory and hasattr(memory, "retriever"):
            try:
                query_for_retrieval = state.get("original_query", "") + " ".join(msg.content for msg in clean_history)
                retrieved_docs = memory.retriever.invoke(query_for_retrieval)
                if retrieved_docs:
                    retrieved_memory_str = (
                        "You have the following potentially relevant information from a previous conversation:\n"
                        "--- START OF RETRIEVED MEMORY ---\n"
                        f"{retrieved_docs[0].page_content}\n"
                        "--- END OF RETRIEVED MEMORY ---\n"
                        "Use this information ONLY if it is relevant to the current query. Otherwise, ignore it."
                    )
            except Exception as e:
                print(f"Memory retrieval error: {e}")
                retrieved_memory_str = ""
        else:
            retrieved_memory_str = ""

        # 3. Prepare the tools and prompt for the agent.
        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in clean_history])
        
        if tool_names is not None:
            tools_for_agent = {name: TOOL_MAP[name] for name in tool_names if name in TOOL_MAP}
        else:
            tools_for_agent = TOOL_MAP

        agent_instance = ReActAgent(tools_for_agent)

        task_description = "handle a general user request that did not fit a specific category" if agent_name == "general" else agent_name.replace("_", " ")

        current_time = state.get("current_time", "Not available. Please ask the user for the current date if needed.")
        formatted_base_prompt = BASE_PROMPT.format(current_time=current_time)

        focused_prompt_str = FOCUSED_TASK_PROMPT.format(
            intent_name=task_description,
            conversation_history=history_str
        )

        messages_for_agent = [
            SystemMessage(content=f"{formatted_base_prompt}\n\n{retrieved_memory_str}\n\n{focused_prompt_str}")
        ] + clean_history

        # 4. Run the agent.
        agent_sub_state = {"messages": messages_for_agent}
        result_state = agent_instance(agent_sub_state)
        agent_output = result_state.get('output', 'No output from agent.')

        # 5. Save the current interaction to long-term memory if memory is valid.
        if memory and hasattr(memory, "save_context"):
            try:
                memory.save_context(
                    {"input": state.get("original_query", "")},
                    {"output": agent_output}
                )
            except Exception as e:
                print(f"Memory save_context error: {e}")

        # 6. Return only the new information this node generated.
        return {
            "output": agent_output,
            "last_completed_intent": agent_name,
        }
    return agent_runner

def summarizer_node(state: AgentState) -> AgentState:
    """
    Synthesizes the aggregated output into a final response.
    """
    aggregated_response = state.get("aggregated_output", "")
    user_query = state.get("original_query", state['messages'][-1].content)

    summarization_prompt_str = SUMMARIZER_PROMPT.format(
        user_query=user_query,
        aggregated_response=aggregated_response
    )

    final_response = SHARED_LLM.invoke(summarization_prompt_str).content
    
    # Get the full message history from the state
    history = state.get("messages", [])
    
    # Return the full history plus the new final response, which the app layer expects.
    return {
        "aggregated_output": final_response,
        "messages": history + [AIMessage(content=final_response)],
    }
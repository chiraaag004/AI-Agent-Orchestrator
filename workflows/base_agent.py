from langgraph.prebuilt import create_react_agent
from config.llm_loader import load_llm
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class ReActAgent:
    def __init__(self, tools):
        """
        Initializes a ReAct agent with a given set of tools.

        Args:
            tools (dict): A dictionary of tools available to the agent.
        """
        self.llm = load_llm()
        self.agent = create_react_agent(model=self.llm, tools=list(tools.values()))

    def __call__(self, state: dict) -> dict:
        """
        Executes the agent with the user's input from the state.

        Args:
            state (dict): The current state of the graph.

        Returns:
            dict: The updated state with the agent's 'output'.
        """
        try:
            # Sanitize the history to prevent confusion from old tool calls.
            # This ensures we only pass the text content of user and AI messages,
            # stripping any other message types (like ToolMessage) that might confuse the agent.
            # It's crucial to include SystemMessage here so the agent gets its instructions.
            conversation_history = state.get("messages", [])
            clean_history = [
                type(msg)(content=msg.content) for msg in conversation_history
                if isinstance(msg, (HumanMessage, AIMessage, SystemMessage))
            ]

            # The agent expects the system prompt to be part of the messages list.
            result = self.agent.invoke({"messages": clean_history})
            return {"output": result['messages'][-1].content}
        except Exception as e:
            logging.error(f"Error in ReActAgent: {e}", exc_info=True)
            return {"output": "I encountered an error. Please try again."}

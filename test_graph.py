import sys
import os
from pprint import pprint

# This ensures that the script can find the other modules in the project
# when run from the root 'ai_hackathon' directory.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from hospitalitybot.graph import travel_graph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from workflows.language_helpers import detect_language, translate_text
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from typing import List

def run_interactive_session():
    """
    Runs an interactive session with the agent, maintaining conversation history
    by passing the full message list back into the graph on each turn.
    """
    # This dictionary will hold the state that persists between turns.
    session_state = {
        "messages": [],
        "detected_language": None, # Start with no language detected
    }

    # Instantiate the Langfuse handler. It will automatically read credentials
    # from your environment variables. 
    langfuse_client = get_client()

    print("✅ Agent is ready. Type 'exit' to quit.")

    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break

        # The handler will automatically create a trace for each invocation.
        langfuse_handler = CallbackHandler()

        # 1. Detect language for the session, making non-English "sticky".
        session_language = session_state.get("detected_language")
        current_language = detect_language(query)
        if session_language and session_language != 'en':
            final_language = session_language
        else:
            final_language = current_language
        session_state["detected_language"] = final_language

        # 2. Translate user input to English for the agent.
        english_query = translate_text(query, target_language="english") if final_language != 'en' else query

        # 3. Add the English-translated message to the history.
        session_state["messages"].append(HumanMessage(content=english_query))

        # 4. Prepare the input for the graph. It gets the full state, plus the
        # original untranslated query for context in the summarizer.
        graph_input = {**session_state, "original_query": query}

        # The config dictionary is where we pass the callback handler.
        config = {"callbacks": [langfuse_handler]}

        print("🤖 Agent is thinking...")

        # 5. Invoke the graph, which now operates entirely in English.
        result = travel_graph.invoke(graph_input, config=config)

        # 6. Update the session's message history from the graph's final state.
        session_state["messages"] = result["messages"]
        english_ai_response = session_state["messages"][-1].content

        # 7. Translate the agent's English response back to the user's language for display.
        display_response = translate_text(
            english_ai_response,
            target_language=final_language,
            original_query=query
        ) if final_language != 'en' else english_ai_response
        
        print(f"\nAgent: {display_response}\n")

if __name__ == "__main__":
    run_interactive_session()
    print("✅ Session ended.")
    

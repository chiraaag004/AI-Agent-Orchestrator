import sys
import os
import streamlit as st
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

# This ensures that the script can find the other modules in the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.atca.graph import travel_graph
from langchain_core.messages import HumanMessage, AIMessage
from workflows.language_helpers import detect_language, translate_text
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Load environment variables from .env file
load_dotenv()

# --- Langfuse Configuration ---
# Initialize once and store in session state if not already present
if "langfuse_handler" not in st.session_state:
    try:
        # The handler will be created for each trace, but the client is persistent.
        st.session_state.langfuse_client = get_client()
        st.session_state.langfuse_enabled = True
    except Exception as e:
        st.session_state.langfuse_enabled = False
        st.sidebar.warning(f"Langfuse not configured: {e}")


def initialize_session_state():
    """Initializes the session state for the chat."""
    if "messages" not in st.session_state:
        # This holds the display messages in their original language
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI Travel Companion. How can I help you plan your trip?"}
        ]
    if "graph_state" not in st.session_state:
        # This holds the state for the LangGraph agent (always in English)
        st.session_state.graph_state = {
            "messages": [],
            "detected_language": None,
        }

def display_chat_history():
    """Displays the chat history from st.session_state.messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input():
    """Handles user input, runs the graph, and manages state."""
    prompt = st.chat_input("Ask about your travel plans...")
    if not prompt:
        return

    # Display user message in the chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Language Handling ---
    session_language = st.session_state.graph_state.get("detected_language")
    current_language = detect_language(prompt)
    # Make non-English "sticky" for the session
    final_language = session_language if session_language and session_language != 'en' else current_language
    st.session_state.graph_state["detected_language"] = final_language

    # Translate query to English for the agent
    english_query = translate_text(prompt, target_language="english") if final_language != 'en' else prompt
    st.session_state.graph_state["messages"].append(HumanMessage(content=english_query))

    # --- Agent Invocation ---
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent is thinking..."):
            config = {}
            if st.session_state.get("langfuse_enabled"):
                config["callbacks"] = [CallbackHandler()]

            # Prepare input for the graph
            graph_input = {**st.session_state.graph_state, "original_query": prompt}

            # Invoke the graph
            result = travel_graph.invoke(graph_input, config=config)

            # --- FIX: Append the new AI message to the history ---
            # The result from the graph contains the final state of the conversation for THIS turn.
            # The last message in that state is the new AI response.
            new_ai_message = result["messages"][-1]
            st.session_state.graph_state["messages"].append(new_ai_message)

            # Translate response back to user's language
            english_ai_response = new_ai_message.content
            display_response = translate_text(
                english_ai_response, target_language=final_language, original_query=prompt
            ) if final_language != 'en' else english_ai_response

            st.markdown(display_response)
            st.session_state.messages.append({"role": "assistant", "content": display_response})

def download_chat_history():
    """Provides a button to download the chat history."""
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        chat_export_data = pd.DataFrame(st.session_state.messages).to_csv(index=False)
        st.sidebar.download_button("Download Chat History", chat_export_data, "chat_history.csv", "text/csv")

# --- App Layout ---
st.set_page_config(page_title="AI Travel Companion", page_icon="✈️")
st.title("✈️ AI Travel Companion")
st.caption("Your personal agent for planning the perfect trip.")

initialize_session_state()
display_chat_history()
handle_user_input()
download_chat_history()
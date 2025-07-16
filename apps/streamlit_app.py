import sys
import os
import streamlit as st
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

# This ensures that the script can find the other modules in the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hospitalitybot.graph import hospitality_graph
from langchain_core.messages import HumanMessage, AIMessage
from workflows.language_helpers import detect_language, translate_text
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from utils.memory_setup import create_long_term_memory
from config.settings import CONVERSATION_WINDOW_SIZE
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- Langfuse Configuration ---
# Initialize once and store in session state if not already present
if "langfuse_enabled" not in st.session_state:
    try:
        # Check if Langfuse can be initialized. The CallbackHandler will create its
        # own client internally using the same environment variables.
        get_client()
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
            "memory": None,
        }
    # Initialize Long-Term Memory once per session
    if "long_term_memory" not in st.session_state:
        try:
            # This embedding model should correspond to your LLM provider
            embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "models/embedding-001")
            embedding_model = GoogleGenerativeAIEmbeddings(model=embedding_model_name)
            st.session_state.long_term_memory = create_long_term_memory(embedding_model)
        except Exception as e:
            st.sidebar.error(f"Could not initialize memory: {e}")
            st.session_state.long_term_memory = None

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

            # Prepare the input for the graph for this specific turn.
            # Start with a copy of the full agent state.
            graph_input = st.session_state.graph_state.copy()
            
            # Add turn-specific data.
            graph_input["original_query"] = prompt
            graph_input["memory"] = st.session_state.long_term_memory

            # IMPORTANT: Enforce the conversation window. This ensures all nodes in the graph
            # (including routers) operate on a consistent, limited view of the history,
            # preventing context overflow and keeping token usage predictable.
            graph_input["messages"] = graph_input["messages"][-CONVERSATION_WINDOW_SIZE:]

            try:
                # Invoke the graph with the prepared, windowed input
                result = hospitality_graph.invoke(graph_input, config=config)

                # Translate response back to user's language
                # The result from the graph contains the new AI message. We should not assume it
                # contains the full history. The new message is the last one in the list.
                # We append this new message to our canonical history to preserve the conversation.
                if "messages" in result and result["messages"] and isinstance(result["messages"][-1], AIMessage):
                    new_ai_message = result["messages"][-1]
                    # Append the new AI message to our canonical agent state history.
                    st.session_state.graph_state["messages"].append(new_ai_message)
                    english_ai_response = new_ai_message.content
                    display_response = translate_text(
                        english_ai_response, target_language=final_language, original_query=prompt
                    ) if final_language != 'en' else english_ai_response
                else:
                    display_response = "Sorry, no response was generated."

                st.markdown(display_response)
                st.session_state.messages.append({"role": "assistant", "content": display_response})
            except Exception as e:
                error_message = "Sorry, I encountered an error while processing your request. Please try again."
                st.error(error_message)
                print(f"Agent invocation error: {e}\nGraph input: {graph_input}")
                st.session_state.messages.append({"role": "assistant", "content": error_message})

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
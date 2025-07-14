import sys
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timezone
from dotenv import load_dotenv

# This ensures that the script can find the other modules in the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.atca.graph import travel_graph
from langchain_core.messages import HumanMessage, AIMessage
from workflows.language_helpers import detect_language, translate_text
from utils.memory_setup import create_long_term_memory
from config.settings import CONVERSATION_WINDOW_SIZE
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- App Initialization ---
app = Flask(__name__)

# --- Session and Memory Management ---
# In a production environment, use a more persistent store like Redis or a database.
# For this example, we use a simple in-memory dictionary.
user_sessions = {}

def get_or_create_session(session_id: str):
    """
    Retrieves an existing user session or creates a new one.
    A session includes the agent's state and long-term memory.
    """
    if session_id not in user_sessions:
        print(f"Creating new session for {session_id}")
        try:
            embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "models/embedding-001")
            embedding_model = GoogleGenerativeAIEmbeddings(model=embedding_model_name)
            long_term_memory = create_long_term_memory(embedding_model)
        except Exception as e:
            print(f"Fatal Error: Could not initialize memory for {session_id}. Error: {e}")
            long_term_memory = None

        user_sessions[session_id] = {
            "graph_state": {
                "messages": [],
                "detected_language": None,
            },
            "long_term_memory": long_term_memory,
        }
    return user_sessions[session_id]

# --- Twilio Webhook ---
@app.route("/sms", methods=['POST'])
def sms_reply():
    """
    Main webhook to handle incoming SMS messages from Twilio.
    """
    # 1. Extract sender and message from the incoming request
    from_number = request.values.get('From', None)
    prompt = request.values.get('Body', None)
    print(f"Incoming message from {from_number}: {prompt}")

    # 2. Get or create the user's session state
    session = get_or_create_session(from_number)
    graph_state = session["graph_state"]
    long_term_memory = session["long_term_memory"]

    # 3. Language Handling
    session_language = graph_state.get("detected_language")
    current_language = detect_language(prompt)
    final_language = session_language if session_language and session_language != 'en' else current_language
    graph_state["detected_language"] = final_language

    # Translate query to English for the agent
    english_query = translate_text(prompt, target_language="english") if final_language != 'en' else prompt
    graph_state["messages"].append(HumanMessage(content=english_query))

    # 4. Prepare Graph Input and Invoke Agent
    graph_input = graph_state.copy()
    graph_input["original_query"] = prompt
    graph_input["memory"] = long_term_memory
    graph_input["messages"] = graph_input["messages"][-CONVERSATION_WINDOW_SIZE:]
    graph_input["current_time"] = datetime.now(timezone.utc).isoformat()

    try:
        # Invoke the graph with the prepared, windowed input
        result = travel_graph.invoke(graph_input)

        if "messages" in result and result["messages"] and isinstance(result["messages"][-1], AIMessage):
            new_ai_message = result["messages"][-1]
            # Append the new AI message to our canonical agent state history.
            graph_state["messages"].append(new_ai_message)
            english_ai_response = new_ai_message.content
            display_response = translate_text(
                english_ai_response, target_language=final_language, original_query=prompt
            ) if final_language != 'en' else english_ai_response
        else:
            display_response = "Sorry, I encountered a problem and could not generate a response."

    except Exception as e:
        print(f"Agent invocation error for {from_number}: {e}\nGraph input: {graph_input}")
        display_response = "Sorry, I encountered an error while processing your request. Please try again."

    # 5. Send the response back to the user via Twilio
    twilio_response = MessagingResponse()
    twilio_response.message(display_response)

    return str(twilio_response)

if __name__ == "__main__":
    print("Starting Twilio AI Travel Companion server...")
    print("Ensure you have ngrok running and your Twilio webhook configured.")
    app.run(debug=True, use_reloader=False, port=5000)
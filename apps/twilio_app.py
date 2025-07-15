import sys
import os
import io
import tempfile
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

# Project path configuration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Custom imports
from hospitalitybot.graph import hospitality_graph
from langchain_core.messages import HumanMessage, AIMessage
from workflows.language_helpers import detect_language, translate_text
from utils.memory_setup import create_long_term_memory
from config.settings import CONVERSATION_WINDOW_SIZE
from utils.voice_services import SpeechToTextManager, TextToSpeechManager
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# Speech modules
stt_manager = SpeechToTextManager()
tts_manager = TextToSpeechManager()

# In-memory session store (replace with Redis/db for prod)
user_sessions = {}

def get_or_create_session(session_id: str):
    if session_id not in user_sessions:
        print(f"Creating new session for {session_id}")
        try:
            embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "models/embedding-001")
            embedding_model = GoogleGenerativeAIEmbeddings(model=embedding_model_name)
            long_term_memory = create_long_term_memory(embedding_model)
        except Exception as e:
            print(f"Fatal Error initializing memory for {session_id}: {e}")
            long_term_memory = None

        user_sessions[session_id] = {
            "graph_state": {
                "messages": [],
                "detected_language": None,
            },
            "long_term_memory": long_term_memory,
        }
    return user_sessions[session_id]

@app.route("/sms", methods=['POST'])
def sms_reply():
    from_number = request.values.get("From", None)
    text_message = request.values.get("Body", None)
    media_url = request.values.get("MediaUrl0", None)

    session = get_or_create_session(from_number)
    graph_state = session["graph_state"]
    long_term_memory = session["long_term_memory"]

    try:
        # 1. Handle input (voice or text)
        if media_url:
            print(f"Audio message received from {from_number}")
            audio_response = requests.get(media_url)
            audio_content = io.BytesIO(audio_response.content)
            user_query = stt_manager.transcribe_audio(audio_content.read())
            prompt = user_query or "I sent an audio message that couldn't be transcribed."
        else:
            prompt = text_message or "No message received."

        print(f"User Query from {from_number}: {prompt}")

        # 2. Detect language
        session_language = graph_state.get("detected_language")
        current_language = detect_language(prompt)
        final_language = session_language if session_language and session_language != "en" else current_language
        graph_state["detected_language"] = final_language

        english_query = translate_text(prompt, target_language="english") if final_language != "en" else prompt
        graph_state["messages"].append(HumanMessage(content=english_query))

        # 3. Prepare graph input
        graph_input = {
            **graph_state,
            "original_query": prompt,
            "memory": long_term_memory,
            "messages": graph_state["messages"][-CONVERSATION_WINDOW_SIZE:],
            "current_time": datetime.now(timezone.utc).isoformat()
        }

        # 4. Invoke graph
        result = hospitality_graph.invoke(graph_input)

        if result.get("messages") and isinstance(result["messages"][-1], AIMessage):
            new_ai_message = result["messages"][-1]
            graph_state["messages"].append(new_ai_message)
            english_ai_response = new_ai_message.content
            display_response = translate_text(
                english_ai_response, target_language=final_language, original_query=prompt
            ) if final_language != "en" else english_ai_response
        else:
            display_response = "Sorry, I couldn't generate a response."

    except Exception as e:
        print(f"Error processing message from {from_number}: {e}")
        display_response = "Sorry, there was an error processing your message."

    # 5. Generate audio response (if voice input or short reply)
    try:
        audio_url = None
        if media_url or len(display_response) < 100:
            audio_chunks = list(tts_manager.synthesize(display_response))
            full_audio = b"".join(audio_chunks)
            if full_audio:
                with tempfile.NamedTemporaryFile(suffix=".mulaw", delete=False) as temp_audio_file:
                    temp_audio_file.write(full_audio)
                    temp_audio_path = temp_audio_file.name
                audio_url = f"http://a72b-103-106-239-6.ngrok-free.app/temp_audio/{os.path.basename(temp_audio_path)}"
    except Exception as e:
        print(f"Audio generation failed: {e}")
        audio_url = None

    # 6. Send Twilio response
    twilio_response = MessagingResponse()
    if audio_url:
        twilio_response.message().media(audio_url)
    else:
        twilio_response.message(display_response)

    return str(twilio_response)

if __name__ == "__main__":
    print("🚀 Starting Twilio Hospitality Bot Server...")
    app.run(debug=True, use_reloader=False, port=5000)

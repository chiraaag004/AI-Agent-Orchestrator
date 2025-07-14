import sys
import os
import json
import base64
import asyncio
import time
from flask import Flask, request
from flask_sock import Sock
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
from datetime import datetime, timezone
from config.settings import SILENCE_THRESHOLD_S

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.aica.graph import aica_graph
from langchain_core.messages import HumanMessage, AIMessage
from utils.voice_services import SpeechToTextManager, TextToSpeechManager
from apps.atca_twilio_app import get_or_create_session # Reusing session logic
from config.settings import CONVERSATION_WINDOW_SIZE

# Load environment variables
load_dotenv()

app = Flask(__name__)
sock = Sock(app)

# --- AICA Application ---

@app.route("/voice", methods=['POST'])
def voice_webhook():
    """
    This webhook is the entry point for all incoming Twilio voice calls.
    It responds with TwiML to establish a WebSocket stream.
    """
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"wss://{request.host}/stream")
    response.append(connect)
    print("Incoming call... establishing WebSocket stream.")
    return str(response), 200, {'Content-Type': 'text/xml'}

@sock.route("/stream")
async def stream(ws):
    """
    This is the WebSocket handler for the real-time audio stream.
    """
    print("WebSocket connection established.")
    stt_manager = SpeechToTextManager()
    tts_manager = TextToSpeechManager()
    
    session_id = "voice_session_" + os.urandom(8).hex()
    session = get_or_create_session(session_id)
    graph_state = session["graph_state"]
    long_term_memory = session["long_term_memory"]

    def send_audio_to_twilio(audio_generator, stream_sid):
        """Helper function to send synthesized audio chunks back to Twilio."""
        for audio_out_chunk in audio_generator:
            media_response = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": base64.b64encode(audio_out_chunk).decode('utf-8')
                }
            }
            ws.send(json.dumps(media_response))

    async def handle_interaction(transcribed_text, stream_sid):
        """
        Handles the full interaction flow: acknowledge, process, and respond.
        This runs as a concurrent task to keep the main loop responsive.
        """
        # 1. Acknowledge the user immediately
        ack_text = "Okay, one moment while I check on that."
        print(f"Acknowledging user: '{ack_text}'")
        ack_audio_generator = tts_manager.synthesize(ack_text)
        # Run the acknowledgement in a separate thread so it doesn't block agent processing
        ack_task = asyncio.to_thread(send_audio_to_twilio, ack_audio_generator, stream_sid)

        # 2. Invoke Agent Brain in the background
        print("Invoking agent in background...")
        graph_state["messages"].append(HumanMessage(content=transcribed_text))
        graph_input = graph_state.copy()
        graph_input["original_query"] = transcribed_text
        graph_input["memory"] = long_term_memory
        graph_input["messages"] = graph_input["messages"][-CONVERSATION_WINDOW_SIZE:]
        graph_input["current_time"] = datetime.now(timezone.utc).isoformat()

        try:
            # Run the synchronous, blocking agent call in a thread
            result = await asyncio.to_thread(aica_graph.invoke, graph_input)
            # Use the robust result extraction logic from aica_app.py
            ai_response_text = result.get("aggregated_output", "I'm sorry, I couldn't generate a response.")
            graph_state["messages"].append(AIMessage(content=ai_response_text))
        except Exception as e:
            print(f"Agent invocation error: {e}")
            ai_response_text = "I'm sorry, I encountered an error."

        # 3. Deliver Final Response (after acknowledgement is complete)
        await ack_task
        print(f"Agent response: '{ai_response_text}'")
        final_audio_generator = tts_manager.synthesize(ai_response_text)
        await asyncio.to_thread(send_audio_to_twilio, final_audio_generator, stream_sid)

    # --- Main Interaction Loop ---
    audio_buffer = b''
    last_audio_time = time.time()
    stream_sid = None

    while ws.connected:
        try:
            # Run the blocking receive call in a thread to not block the event loop
            message = await asyncio.to_thread(ws.receive, timeout=0.1)
        except Exception:
            message = None

        # If no message, check for silence timeout to trigger transcription
        if message is None:
            is_silent = (time.time() - last_audio_time) > SILENCE_THRESHOLD_S
            if audio_buffer and is_silent:
                print(f"Silence detected. Transcribing {len(audio_buffer)} bytes.")
                transcribed_text = stt_manager.transcribe_audio(audio_buffer)
                audio_buffer = b'' # Clear buffer after transcription

                if transcribed_text:
                    print(f"Transcription received: '{transcribed_text}'")
                    # Fire-and-forget the interaction task to keep the loop non-blocking
                    asyncio.create_task(handle_interaction(transcribed_text, stream_sid))
            continue

        # If a message is received, process it
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode WebSocket message: {message}")
            continue

        event = data.get('event')

        if event == 'start':
            stream_sid = data['start']['streamSid']
            print(f"Twilio start stream event received (SID: {stream_sid}).")
            # Play a welcome message at the start of the call
            welcome_text = "Hello, and thank you for calling. How can I help you today?"
            audio_generator = tts_manager.synthesize(welcome_text)
            send_audio_to_twilio(audio_generator, stream_sid)

        elif event == 'media':
            if stream_sid is None:
                stream_sid = data['streamSid']
            
            try:
                # The audio payload is base64 encoded.
                audio_chunk = base64.b64decode(data['media']['payload'])
                audio_buffer += audio_chunk
                last_audio_time = time.time()
            except Exception as e:
                print(f"Error processing media payload: {e}")

        elif event == 'stop':
            print("Twilio stop stream event received.")
            break

    print("WebSocket connection closed.")

if __name__ == "__main__":
    print("Starting AI Inquiry Call Agent (AICA) server...")
    print("Ensure you have ngrok running and your Twilio webhook configured for VOICE.")
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
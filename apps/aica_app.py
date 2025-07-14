import sys
import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timezone
from pydub import AudioSegment
import io
import audioop
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.aica.graph import aica_graph
from langchain_core.messages import HumanMessage, AIMessage
from utils.voice_services import SpeechToTextManager, TextToSpeechManager
from apps.atca_twilio_app import get_or_create_session
from config.settings import CONVERSATION_WINDOW_SIZE

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="AICA Test App", page_icon="📞")
st.title("📞 AICA Voice Integration Test")
st.caption("Upload a WAV or MP3 file to test the voice agent.")

session_id = "streamlit_test_session"
if "session" not in st.session_state:
    st.session_state.session = get_or_create_session(session_id)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "stt_manager" not in st.session_state:
    st.session_state.stt_manager = SpeechToTextManager()
if "tts_manager" not in st.session_state:
    st.session_state.tts_manager = TextToSpeechManager()

def display_chat_history():
    """Displays the chat history using st.chat_message for a better UI."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if there's an audio component to display
            if "audio" in message and message["audio"] is not None:
                st.markdown(message["content"])
                # Convert mu-law to PCM WAV for playback
                try:
                    mulaw_bytes = message["audio"]["data"]
                    sample_rate = message["audio"]["sample_rate"]
                    # Convert mu-law to PCM
                    pcm_bytes = audioop.ulaw2lin(mulaw_bytes, 2)
                    # Create WAV header
                    import wave
                    wav_io = io.BytesIO()
                    with wave.open(wav_io, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(pcm_bytes)
                    wav_io.seek(0)
                    st.audio(wav_io.read(), format="audio/wav", sample_rate=sample_rate)
                except Exception as e:
                    st.warning(f"Audio playback failed: {e}")
            else:
                st.markdown(message["content"])

def convert_audio_to_mulaw(audio_file):
    """Converts an uploaded audio file to mu-law format if necessary."""
    audio_bytes = audio_file.read()
    if audio_file.type == "audio/x-mulaw":
        return audio_bytes

    try:
        st.info(f"Converting {audio_file.type} to the required mu-law format...")
        audio_stream = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(audio_stream)
        audio_segment = audio_segment.set_frame_rate(8000).set_channels(1)
        # Convert to PCM 16-bit mono
        pcm_bytes = audio_segment.raw_data
        sample_width = audio_segment.sample_width
        # Convert PCM to mu-law
        mulaw_bytes = audioop.lin2ulaw(pcm_bytes, sample_width)
        return mulaw_bytes
    except Exception as e:
        st.error(f"Failed to convert audio file. Please try a standard WAV or MP3 file. Error: {e}")
        return None

def run_agent_and_get_response(user_query):
    """Invokes the agent graph and returns the AI's text response."""
    graph_state = st.session_state.session["graph_state"]
    graph_state["messages"].append(HumanMessage(content=user_query))

    graph_input = graph_state.copy()
    graph_input["original_query"] = user_query
    graph_input["memory"] = st.session_state.session.get("long_term_memory")
    graph_input["messages"] = graph_input["messages"][-CONVERSATION_WINDOW_SIZE:]
    graph_input["current_time"] = datetime.now(timezone.utc).isoformat()

    try:
        result = aica_graph.invoke(graph_input)
        # Extract the final response from the 'aggregated_output' key as per the agent's design.
        # Provide a fallback message if the key is missing.
        ai_response_text = result.get(
            "aggregated_output", "I'm sorry, I couldn't generate a response."
        )
        graph_state["messages"].append(AIMessage(content=ai_response_text))
        return ai_response_text
    except Exception as e:
        st.error(f"Agent processing error: {e}")
        return "I'm sorry, I encountered an error."

def handle_audio_upload(audio_file):
    """Orchestrates the entire process for an uploaded audio file."""
    with st.spinner("Processing audio..."):
        # 1. Convert and Transcribe using the cached manager
        stt_manager = st.session_state.stt_manager
        mulaw_audio = convert_audio_to_mulaw(audio_file)
        if not mulaw_audio:
            return

        user_query = stt_manager.transcribe_audio(mulaw_audio)
        if not user_query:
            st.warning("Could not understand the audio. Please try again with a clearer recording.")
            return

        # Add user's transcribed message to chat
        st.session_state.messages.append({"role": "user", "content": f"🎤: {user_query}"})

        # 2. Run Agent
        ai_response_text = run_agent_and_get_response(user_query)

        # 3. Synthesize and Display Response using the cached manager
        tts_manager = st.session_state.tts_manager
        try:
            audio_chunks = list(tts_manager.synthesize(ai_response_text))
            full_audio = b"".join(audio_chunks)
        except Exception as e:
            st.error(f"Text-to-speech synthesis failed: {e}")
            full_audio = b""

        if not full_audio:
            st.warning("No audio was generated for the response.")

        # Add AI's response with audio to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"🤖: {ai_response_text}",
            "audio": {
                "data": full_audio,
                "format": "audio/x-mulaw",
                "sample_rate": 8000
            } if full_audio else None
        })

# --- Main App Logic ---
display_chat_history()

uploaded_file = st.file_uploader("Upload an audio file (WAV or MP3)", type=["wav", "mp3", "mulaw"])
if uploaded_file:
    handle_audio_upload(uploaded_file)
    st.rerun()

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.session["graph_state"]["messages"] = []
    st.rerun()
import os
import io
import json
import wave
import whisper
import logging
import audioop
import torch
import tempfile
from datetime import datetime
from typing import Generator
from pathlib import Path
from onnxruntime import InferenceSession
from piper.config import PiperConfig
from piper.voice import PiperVoice, AudioChunk
from config.settings import PIPER_VOICE_MODEL_PATH, WHISPER_MODEL_NAME, WHISPER_DOWNLOAD_ROOT

class SpeechToTextManager:
    """
    Manages speech-to-text transcription using Whisper.
    Offline and singleton model loader.
    """
    _instance = None
    _model = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SpeechToTextManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.logger = logging.getLogger(self.__class__.__name__)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_fp16 = device == "cuda"

        try:
            self.logger.info(f"Loading Whisper model: {WHISPER_MODEL_NAME} on {device}...")
            self._model = whisper.load_model(
                WHISPER_MODEL_NAME,
                download_root=WHISPER_DOWNLOAD_ROOT,
                device=device
            )
            self.logger.info("✅ Whisper model loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}", exc_info=True)

    def transcribe_audio(self, audio_data: bytes, suffix: str = ".wav") -> str | None:
        """
        Transcribes mu-law encoded audio data using Whisper (via temp WAV).
        """
        if not audio_data:
            return None

        try:
            # Save to temporary WAV file (required by whisper)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            # Optional debug save
            debug_dir = "debug_audio"
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, f"received_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}")
            with open(debug_file, "wb") as f:
                f.write(audio_data)

            # Transcribe from file path
            result = self._model.transcribe(temp_audio_path, fp16=self.use_fp16)
            transcript = result.get("text", "").strip()

            self.logger.info(f"Transcription result: '{transcript}'")
            os.remove(temp_audio_path)
            return transcript

        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}", exc_info=True)
            return None


class TextToSpeechManager:
    """
    Manages text-to-speech using Piper (ONNX).
    Returns mu-law audio at 8kHz for telephony.
    """
    _instance = None
    _voice = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TextToSpeechManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.logger = logging.getLogger(self.__class__.__name__)
        model_path = Path(PIPER_VOICE_MODEL_PATH)
        config_path = Path(f"{PIPER_VOICE_MODEL_PATH}.json")

        if not model_path.is_file():
            raise FileNotFoundError(
                f"Piper voice model not found at: {model_path}. "
                "Download models from: https://huggingface.co/rhasspy/piper-voices/tree/main"
            )

        if not config_path.is_file():
            raise FileNotFoundError(
                f"Missing Piper config file: {config_path}"
            )

        try:
            self.logger.info("Loading Piper TTS model...")
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            self.config = PiperConfig.from_dict(config_dict)
            session = InferenceSession(str(model_path))
            self._voice = PiperVoice(session, self.config)
            self.logger.info("✅ Piper voice model loaded successfully.")
        except Exception as e:
            self.logger.error(f"Piper model loading error: {e}", exc_info=True)

    def synthesize(self, text: str) -> Generator[bytes, None, None]:
        """
        Yields 8kHz mu-law encoded audio chunks from input text using Piper.
        """
        in_rate = self.config.sample_rate
        sample_width = 2  # 16-bit PCM
        n_channels = 1    # mono

        try:
            for audio_chunk in self._voice.synthesize(text):
                if not isinstance(audio_chunk, AudioChunk):
                    self.logger.error("Unexpected object from Piper.")
                    continue

                resampled_pcm, _ = audioop.ratecv(
                    audio_chunk.audio_int16_bytes, sample_width, n_channels, in_rate, 8000, None
                )
                mulaw_chunk = audioop.lin2ulaw(resampled_pcm, sample_width)
                yield mulaw_chunk
        except Exception as e:
            self.logger.error(f"Piper synthesis error: {e}", exc_info=True)

import os
import io
import json
import wave
import whisper
import logging
import audioop
import torch
import numpy as np
from typing import Generator
from pathlib import Path
from onnxruntime import InferenceSession
from piper.config import PiperConfig
from piper.voice import PiperVoice, AudioChunk
from config.settings import PIPER_VOICE_MODEL_PATH, WHISPER_MODEL_NAME, WHISPER_DOWNLOAD_ROOT

class SpeechToTextManager:
    """
    Manages speech-to-text transcription using OpenAI's Whisper.
    This implementation is designed for offline, local processing.
    It's a singleton to prevent reloading the model into memory.
    """
    _instance = None
    _model = None
    use_fp16 = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SpeechToTextManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self.logger = logging.getLogger(self.__class__.__name__)
            # Determine if a GPU is available for FP16 inference, otherwise use CPU with FP32
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.use_fp16 = device == "cuda"

            self.logger.info(f"Loading Whisper STT model: {WHISPER_MODEL_NAME}...")
            self._model = whisper.load_model(
                WHISPER_MODEL_NAME,
                download_root=WHISPER_DOWNLOAD_ROOT,
                device=device
            )
            self.logger.info(f"Whisper STT model loaded on device: '{device}'.")

    def transcribe_audio(self, audio_data: bytes) -> str | None:
        """
        Transcribes a chunk of mu-law encoded audio data using Whisper.
        """
        if not audio_data:
            return None

        try:
            # 1. Convert mu-law audio data to 16-bit linear PCM
            pcm_data = audioop.ulaw2lin(audio_data, 2)

            # 2. Convert the 16-bit PCM data to a float32 NumPy array.
            # Whisper expects a float32 array ranging from -1.0 to 1.0.
            # The pcm_data is 16-bit, so we divide by 32768.0 (the max value of a 16-bit signed int).
            audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0

            # 3. Transcribe using Whisper
            # The audio is at 8000 Hz, but Whisper will resample it to 16000 Hz automatically.
            result = self._model.transcribe(audio_np, language="en", fp16=self.use_fp16)
            transcript = result.get("text", "").strip()

            self.logger.info(f"Whisper transcription: '{transcript}'")
            return transcript
        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}", exc_info=True)
            return None

class TextToSpeechManager:
    """
    Manages text-to-speech synthesis using Piper TTS.
    This implementation is offline and yields audio chunks suitable for streaming.
    It's a singleton to prevent reloading the voice model.
    """
    _instance = None
    _voice = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TextToSpeechManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._voice is None:
            self.logger = logging.getLogger(self.__class__.__name__)
            model_path = Path(PIPER_VOICE_MODEL_PATH)
            config_path = Path(f"{PIPER_VOICE_MODEL_PATH}.json")

            if not model_path.is_file():
                raise FileNotFoundError(
                    f"Piper voice model not found at: {model_path}. "
                    "Please download a voice model from https://huggingface.co/rhasspy/piper-voices/tree/main"
                )
            if not config_path.is_file():
                raise FileNotFoundError(
                    f"Piper voice config file not found at: {config_path}. "
                    "Please ensure the .onnx.json file is present."
                )

            self.logger.info("Loading Piper TTS model...")
            # 1. Load config from JSON
            with open(config_path, "r", encoding="utf-8") as config_file:
                config_dict = json.load(config_file)
            config = PiperConfig.from_dict(config_dict)
            self.config = config  # Store config for later use
            # 2. Load ONNX model and create inference session
            session = InferenceSession(str(model_path))
            # 3. Instantiate PiperVoice with session and config
            self._voice = PiperVoice(session, config)
            self.logger.info("Piper TTS model loaded.")

    def synthesize(self, text: str) -> Generator[bytes, None, None]:
        """
        Synthesizes text sentence-by-sentence and yields 8kHz mu-law encoded audio chunks.

        This method performs the following steps for each sentence:
        1. Calls the Piper model's streaming `synthesize` method to get raw PCM audio.
        2. Resamples the audio chunk from the model's native sample rate (e.g., 22050 Hz)
           down to the 8000 Hz required for telephony.
        3. Converts the 8kHz PCM data to the mu-law format.
        4. Yields the final mu-law data chunk.
        """
        # Get audio properties from the model's configuration.
        # The sample width for PCM audio is 16 bits (2 bytes).
        # The audio is single-channel (mono).
        in_rate = self.config.sample_rate
        sample_width = 2  # 16-bit
        n_channels = 1    # mono

        # Synthesize audio, receiving a raw PCM chunk for each sentence.
        for audio_chunk in self._voice.synthesize(text):
            # The 'synthesize' method yields AudioChunk objects. We need the raw bytes
            # from the .audio_bytes attribute to perform audio operations.
            # Resample the high-quality PCM chunk to 8kHz for telephony.
            resampled_pcm, _ = audioop.ratecv(
                audio_chunk.audio_int16_bytes, sample_width, n_channels, in_rate, 8000, None
            )

            # Convert the 8kHz PCM audio to mu-law format.
            mulaw_chunk = audioop.lin2ulaw(resampled_pcm, sample_width)
            yield mulaw_chunk
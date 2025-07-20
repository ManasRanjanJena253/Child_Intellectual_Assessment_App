import os
import json
import wave
import vosk

SAMPLE_RATE = 16000  # Should match your uploaded audio file sample rate

def _get_model(model_path):
    if not os.path.isdir(model_path):
        raise FileNotFoundError(
            f"Vosk model not found at {model_path}. "
            "Download it from https://alphacephei.com/vosk/models "
            "and unzip it to that path."
        )
    return vosk.Model(model_path)

def record_audio(uploaded_file):
    """Accept a WAV audio file (mono, 16kHz) and return raw audio bytes."""
    with wave.open(uploaded_file, 'rb') as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != SAMPLE_RATE:
            raise ValueError("Uploaded .wav file must be mono, 16-bit, 16kHz.")
        audio_bytes = wf.readframes(wf.getnframes())
    return audio_bytes

def transcribe(audio_bytes, model_path=None):
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-small-en-us-0.15")
        model_path = os.path.abspath(model_path)

    model = _get_model(model_path)
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    rec.AcceptWaveform(audio_bytes)
    result = json.loads(rec.FinalResult())
    return result.get("text", "").lower()

def record_and_transcribe(uploaded_file, model_path=None):
    """Takes an uploaded .wav file, returns transcribed text"""
    audio_bytes = record_audio(uploaded_file)
    return transcribe(audio_bytes, model_path=model_path)

import queue
import sounddevice as sd
import vosk
import json
import os

SAMPLE_RATE = 16000

def _get_model(model_path):
    if not os.path.isdir(model_path):
        raise FileNotFoundError(
            f"Vosk model not found at {model_path}. "
            "Download it from https://alphacephei.com/vosk/models "
            "and unzip it to that path."
        )
    return vosk.Model(model_path)

def record_audio(duration=3):
    """Record mono audio for a given duration and return raw bytes."""
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16', channels=1, callback=callback):
        sd.sleep(int(duration * 1000))
        audio_bytes = b''.join(list(q.queue))
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

def record_and_transcribe(duration=3, model_path=None):
    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-small-en-us-0.15")
        model_path = os.path.abspath(model_path)

    return transcribe(record_audio(duration), model_path=model_path)

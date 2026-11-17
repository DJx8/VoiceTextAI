import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=api_key)


def transcribe_audio_bytes(audio_data, filename):

    if not audio_data:
        raise ValueError("Audio file is empty.")

    start_time = time.perf_counter()

    result = client.audio.transcriptions.create(
        file=(filename, audio_data),
        model="whisper-large-v3",
        response_format="verbose_json",
        temperature=0.0,
    )

    return {
        "success": True,
        "filename": filename,
        "model": "whisper-large-v3",
        "language": result.language,
        "duration_seconds": result.duration,
        "processing_time_seconds": round(time.perf_counter() - start_time, 3),
        "transcription": result.text.strip(),
    }

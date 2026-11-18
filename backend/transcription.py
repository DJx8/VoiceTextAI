import os
import time
import wave
import tempfile
import subprocess
from pathlib import Path

import imageio_ffmpeg
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()

WHISPER_MODEL = "whisper-large-v3"
INDIC_MODEL = "indic-transcribe"


def get_whisper_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env")

    return Groq(api_key=api_key)


def get_indic_client():
    api_key = os.getenv("BODHAN_API_KEY")

    if not api_key:
        raise RuntimeError("BODHAN_API_KEY is missing from .env")

    return OpenAI(base_url="https://api.bodhan.ai/v1", api_key=api_key)


def convert_audio(audio_data, filename):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    suffix = Path(filename).suffix.lower() or ".audio"

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / f"input{suffix}"
        output_path = Path(temp_dir) / "converted.wav"

        input_path.write_bytes(audio_data)

        command = [
            ffmpeg,
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            raise ValueError(
                "Could not process this audio file. " "Please try another audio format."
            ) from error

        with wave.open(str(output_path), "rb") as wav_file:
            duration = wav_file.getnframes() / wav_file.getframerate()

        wav_data = output_path.read_bytes()

    return wav_data, duration


def transcribe_audio_bytes(audio_data, filename, language="auto", model="indic"):
    if not audio_data:
        raise ValueError("Audio file is empty.")

    if model not in {"whisper", "indic"}:
        raise ValueError("Invalid model selection.")

    start_time = time.perf_counter()

    # Convert audio once for either model.
    wav_data, duration = convert_audio(audio_data, filename)

    # =================================
    # MODEL 1: GROQ WHISPER
    # =================================
    if model == "whisper":

        client = get_whisper_client()

        api_start = time.perf_counter()

        result = client.audio.transcriptions.create(
            file=(f"{Path(filename).stem}.wav", wav_data),
            model=WHISPER_MODEL,
            language="en",
            response_format="verbose_json",
            temperature=0.0,
        )

        api_time = time.perf_counter() - api_start

        return {
            "success": True,
            "filename": filename,
            "selected_model": "whisper",
            "model": WHISPER_MODEL,
            "language": "en",
            "requested_language": "en",
            "duration_seconds": round(duration, 2),
            "processing_time_seconds": round(time.perf_counter() - start_time, 3),
            "api_request_time_seconds": round(api_time, 3),
            "transcription": result.text.strip(),
        }

    # =================================
    # MODEL 2: BODHAN INDIC-TRANSCRIBE
    # =================================
    client = get_indic_client()

    api_start = time.perf_counter()

    # Use a temporary directory to avoid Windows file-locking issues.
    with tempfile.TemporaryDirectory() as temp_dir:

        temp_audio_path = Path(temp_dir) / "audio.wav"
        temp_audio_path.write_bytes(wav_data)

        with open(temp_audio_path, "rb") as audio_file:

            request_data = {"model": INDIC_MODEL, "file": audio_file}

            if language and language != "auto":
                request_data["language"] = language

            result = client.audio.transcriptions.create(**request_data)

    api_time = time.perf_counter() - api_start

    return {
        "success": True,
        "filename": filename,
        "selected_model": "indic",
        "model": INDIC_MODEL,
        "language": language,
        "requested_language": language,
        "duration_seconds": round(duration, 2),
        "processing_time_seconds": round(time.perf_counter() - start_time, 3),
        "api_request_time_seconds": round(api_time, 3),
        "transcription": result.text.strip(),
    }

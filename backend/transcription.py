import os
import time
import wave
import tempfile
import subprocess
import logging

from pathlib import Path
from functools import lru_cache

import imageio_ffmpeg
from dotenv import load_dotenv
from groq import Groq
from gradio_client import Client, handle_file

load_dotenv()

logger = logging.getLogger(__name__)

WHISPER_MODEL = "whisper-large-v3"

# Your private Hugging Face Space
INDIC_SPACE_ID = "Deejay888/VoiceText-AI"
INDIC_MODEL = "indic-transcribe-core"

# Existing VoiceText AI language codes -> Space dropdown labels
HF_LANGUAGES = {
    "auto": "Automatic detection",
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ta": "Tamil",
    "te": "Telugu",
}


# ==========================================
# API CLIENTS
# ==========================================


def get_whisper_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    return Groq(
        api_key=api_key,
        timeout=60.0,
        max_retries=1,
    )


@lru_cache(maxsize=1)
def _create_indic_client(token):
    return Client(
        INDIC_SPACE_ID,
        token=token,
        verbose=False,
        max_workers=2,
        httpx_kwargs={"timeout": 300.0},
    )


def get_indic_client():
    token = os.getenv("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is missing from environment.")

    try:
        return _create_indic_client(token)
    except Exception as error:
        logger.exception("Could not connect to Hugging Face Space.")
        raise RuntimeError(
            "Could not connect to the Indic transcription service."
        ) from error


# ==========================================
# AUDIO CONVERSION
# ==========================================


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
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired as error:
            raise TimeoutError("Audio conversion timed out.") from error
        except subprocess.CalledProcessError as error:
            raise ValueError(
                "Could not process this audio file. " "Please try another audio format."
            ) from error

        with wave.open(str(output_path), "rb") as wav_file:
            duration = wav_file.getnframes() / wav_file.getframerate()

        wav_data = output_path.read_bytes()

    return wav_data, duration


# ==========================================
# MAIN TRANSCRIPTION FUNCTION
# ==========================================


def transcribe_audio_bytes(
    audio_data,
    filename,
    language="auto",
    model="indic",
):
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
    # MODEL 2: HUGGING FACE INDIC
    # =================================

    if language not in HF_LANGUAGES:
        raise ValueError("Unsupported language selection.")

    hf_language = HF_LANGUAGES[language]

    client = get_indic_client()

    api_start = time.perf_counter()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = Path(temp_dir) / "audio.wav"
            temp_audio_path.write_bytes(wav_data)

            # Call the private Space API.
            result = client.predict(
                handle_file(str(temp_audio_path)),
                hf_language,
                api_name="/transcribe",
            )

        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("The transcription service returned no text.")

        transcription = result.strip()

    except Exception as error:
        logger.exception("Hugging Face transcription request failed.")
        raise RuntimeError("Indic transcription failed. Please try again.") from error

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
        "transcription": transcription,
    }

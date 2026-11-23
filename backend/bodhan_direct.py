import io
import json
import logging
import os
import tempfile
import time
from pathlib import Path

import requests

from backend.transcription import convert_audio

logger = logging.getLogger(__name__)

BODHAN_BASE_URL = "https://api.bodhan.ai"

TRANSCRIBE_MODEL = "indic-transcribe"
TRANSLATE_MODEL = "indic-translate"
TTS_MODEL = "indic-speak"


def _get_api_key(environment_name):
    api_key = os.getenv(environment_name)

    if not api_key:
        raise RuntimeError(f"{environment_name} is missing from environment variables.")

    return api_key


def transcribe_with_bodhan(audio_data, filename, language):
    """Transcribe audio into its original regional language."""

    if not audio_data:
        raise ValueError("Audio file is empty.")

    if not language:
        raise ValueError("Please select a spoken language")

    api_key = _get_api_key("BODHAN_TRANSCRIBE_KEY")

    wav_data, duration = convert_audio(audio_data, filename)

    try:
        response = requests.post(
            f"{BODHAN_BASE_URL}/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            data={
                "model": TRANSCRIBE_MODEL,
                **({"language": language} if language != "auto" else {}),
            },
            files={
                "file": (
                    f"{Path(filename).stem}.wav",
                    io.BytesIO(wav_data),
                    "audio/wav",
                )
            },
            timeout=(10, 120),
        )

        response.raise_for_status()
        result = response.json()

        transcription = result.get("text", "").strip()

        if not transcription:
            raise RuntimeError("Bodhan returned an empty transcription.")

        return {
            "transcription": transcription,
            "duration_seconds": round(duration, 2),
            "detected_language": result.get("language")
            or (language if language != "auto" else None),
        }

    except requests.RequestException as error:
        status = (
            error.response.status_code
            if error.response is not None
            else "connection error"
        )
        logger.exception("Bodhan transcription API request failed.")
        raise RuntimeError(
            f"Bodhan transcription request failed ({status})."
        ) from error


def translate_with_bodhan(text, source_language, target_language):
    """Translate text using Bodhan's OpenAI-compatible API."""

    if not text or not text.strip():
        raise ValueError("Text to translate cannot be empty.")

    if not source_language or not target_language:
        raise ValueError("Source and target languages are required.")

    api_key = _get_api_key("BODHAN_TRANSLATE_KEY")

    try:
        response = requests.post(
            f"{BODHAN_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": TRANSLATE_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                "source_language_code": source_language,
                "target_language_code": target_language,
            },
            timeout=(10, 60),
        )

        response.raise_for_status()
        result = response.json()

        translated_text = result["choices"][0]["message"]["content"].strip()

        if not translated_text:
            raise RuntimeError("Bodhan returned an empty translation.")

        return translated_text

    except requests.RequestException as error:
        status = (
            error.response.status_code
            if error.response is not None
            else "connection error"
        )
        logger.exception("Bodhan translation API request failed.")
        raise RuntimeError(f"Bodhan translation request failed ({status}).") from error
    except (KeyError, IndexError, TypeError) as error:
        logger.exception("Unexpected Bodhan translation response.")
        raise RuntimeError(
            "Bodhan returned an unexpected translation response."
        ) from error


def generate_speech_with_bodhan(text, language, voice="Lakshmi"):
    """Generate regional-language speech using Bodhan TTS."""

    if not text or not text.strip():
        raise ValueError("Text for speech generation cannot be empty.")

    if not language or language == "auto":
        raise ValueError("A specific TTS language is required.")

    if not voice or not voice.strip():
        raise ValueError("Please provide a TTS voice.")

    api_key = _get_api_key("BODHAN_SPEAK_KEY")

    try:
        response = requests.post(
            f"{BODHAN_BASE_URL}/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": TTS_MODEL,
                "input": text,
                "voice": voice,
                "instructions": json.dumps({"lang": language}),
            },
            timeout=(10, 120),
        )

        response.raise_for_status()

        if not response.content:
            raise RuntimeError("Bodhan returned an empty audio response.")

        # Keep the generated file available for Gradio playback.
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            prefix="voicetextai_",
            delete=False,
        ) as audio_file:
            audio_file.write(response.content)
            audio_path = audio_file.name

        return audio_path

    except requests.RequestException as error:
        status = (
            error.response.status_code
            if error.response is not None
            else "connection error"
        )
        logger.exception("Bodhan TTS API request failed.")
        raise RuntimeError(f"Bodhan speech generation failed ({status}).") from error


def process_bodhan_direct(
    audio_data,
    filename,
    spoken_language,
    tts_language="ml",
    voice="Lakshmi",
    generate_speech=True,
):
    """
    Complete pipeline:
    Audio -> regional transcription -> English translation
    -> selected regional language -> speech (optional).
    """

    start_time = time.perf_counter()

    # Stage 1: Transcription
    transcription_result = transcribe_with_bodhan(
        audio_data=audio_data,
        filename=filename,
        language=spoken_language,
    )

    regional_text = transcription_result["transcription"]

    # Stage 2: Regional language -> English
    english_text = translate_with_bodhan(
        text=regional_text,
        source_language=spoken_language,
        target_language="en",
    )

    result = {
        "success": True,
        "filename": filename,
        "selected_model": "bodhan_direct",
        "transcription_model": TRANSCRIBE_MODEL,
        "translation_model": TRANSLATE_MODEL,
        "transcription": regional_text,
        "translation": english_text,
        "duration_seconds": transcription_result["duration_seconds"],
        "spoken_language": spoken_language,
        "tts_generated": False,
        "speech_text": "",
        "audio_path": None,
        "tts_error": None,
    }

    # Stage 3: English -> selected regional language -> speech
    if generate_speech:
        try:
            speech_text = translate_with_bodhan(
                text=english_text,
                source_language="en",
                target_language=tts_language,
            )

            audio_path = generate_speech_with_bodhan(
                text=speech_text,
                language=tts_language,
                voice=voice,
            )

            result.update(
                {
                    "tts_generated": True,
                    "tts_model": TTS_MODEL,
                    "tts_language": tts_language,
                    "tts_voice": voice,
                    "speech_text": speech_text,
                    "audio_path": audio_path,
                }
            )

        except Exception as error:
            logger.exception("Optional TTS stage failed.")
            result["tts_error"] = str(error)

    result["processing_time_seconds"] = round(time.perf_counter() - start_time, 3)

    return result

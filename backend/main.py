from pathlib import Path

import gradio as gr
from fastapi import FastAPI, UploadFile, File, HTTPException, Form

from backend.transcription import transcribe_audio_bytes
from frontend.app import demo

app = FastAPI(
    title="VoiceText AI",
    description="Multilingual Speech-to-Text Transcription API",
    version="2.0.0",
)

SUPPORTED_LANGUAGES = {
    "auto",
    "en",
    "as",  # Assamese
    "bn",  # Bengali
    "brx",  # Bodo
    "doi",  # Dogri
    "gu",  # Gujarati
    "hi",  # Hindi
    "kn",  # Kannada
    "ks",  # Kashmiri
    "kok",  # Konkani
    "mai",  # Maithili
    "ml",  # Malayalam
    "mni",  # Manipuri
    "mr",  # Marathi
    "ne",  # Nepali
    "or",  # Odia
    "pa",  # Punjabi
    "sa",  # Sanskrit
    "sat",  # Santali
    "sd",  # Sindhi
    "ta",  # Tamil
    "te",  # Telugu
    "ur",  # Urdu
    "bho",  # Bhojpuri
    "bhb",  # Bhili
}

SUPPORTED_MODELS = {"whisper", "indic"}

SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".webm",
    ".ogg",
    ".flac",
    ".aac",
}


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form("indic"),
    language: str = Form("auto"),
):
    filename = file.filename or "audio.wav"
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio format.")

    if model not in SUPPORTED_MODELS:
        raise HTTPException(
            status_code=400, detail="Invalid model. Choose whisper or indic."
        )

    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language selection.")

    if model == "whisper":
        language = "en"

    audio_data = await file.read()

    if not audio_data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        return transcribe_audio_bytes(
            audio_data=audio_data, filename=filename, language=language, model=model
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/health")
def health():
    return {"status": "running", "application": "VoiceText AI"}


app = gr.mount_gradio_app(app, demo, path="/")

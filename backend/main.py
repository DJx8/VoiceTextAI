from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.transcription import transcribe_audio_bytes
import gradio as gr

app = FastAPI(
    title="VoiceText AI",
    description="AI-powered Speech-to-Text Transcription API",
    version="1.0.0",
)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):

    allowed_types = {
        "audio/mpeg",
        "audio/wav",
        "audio/x-wav",
        "audio/mp4",
        "audio/x-m4a",
        "audio/webm",
        "video/mp4",
        "audio/ogg",
        "audio/flac",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported audio format.")

    audio_data = await file.read()

    if not audio_data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        return transcribe_audio_bytes(audio_data, file.filename or "audio.wav")

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/health")
def health():
    return {"status": "running", "application": "VoiceText AI"}


# Mount Gradio website inside FastAPI
from frontend.app import demo

app = gr.mount_gradio_app(app, demo, path="/")

import os
import gradio as gr

from backend.transcription import transcribe_audio_bytes


def transcribe_audio(uploaded_file, recorded_audio):

    audio_path = uploaded_file or recorded_audio

    if audio_path is None:
        return "", {"success": False, "error": "Please upload or record audio."}

    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        data = transcribe_audio_bytes(audio_data, os.path.basename(audio_path))

        details = {key: value for key, value in data.items() if key != "transcription"}

        return data["transcription"], details

    except Exception as e:
        return "", {"success": False, "error": str(e)}


with gr.Blocks(title="VoiceText AI", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🎙️ VoiceText AI

    ### AI-powered Speech-to-Text Transcription

    Upload an audio file or record your voice.
    """)

    uploaded_file = gr.File(
        label="Upload Audio",
        file_types=[".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac"],
        type="filepath",
    )

    recorded_audio = gr.Audio(
        sources=["microphone"], type="filepath", label="Or Record Your Voice"
    )

    transcribe_btn = gr.Button("🚀 Transcribe Audio", variant="primary")

    transcription_output = gr.Textbox(
        label="Transcription", lines=10, interactive=False
    )

    details_output = gr.JSON(label="Transcription Details")

    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[uploaded_file, recorded_audio],
        outputs=[transcription_output, details_output],
    )

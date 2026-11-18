import os
import gradio as gr

from backend.transcription import transcribe_audio_bytes

MODELS = [
    ("Whisper – English only (Groq)", "whisper"),
    ("Indic-Transcribe – Multilingual (Bodhan)", "indic"),
]

LANGUAGES = [
    ("Automatic Detection", "auto"),
    ("English", "en"),
    ("Kannada (ಕನ್ನಡ)", "kn"),
    ("Malayalam (മലയാളം)", "ml"),
    ("Hindi (हिन्दी)", "hi"),
    ("Tamil (தமிழ்)", "ta"),
    ("Telugu (తెలుగు)", "te"),
]


def transcribe_audio(uploaded_file, recorded_audio, model, language):

    audio_path = uploaded_file or recorded_audio

    if audio_path is None:
        return "", {"success": False, "error": "Please upload or record audio."}

    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        filename = os.path.basename(audio_path)

        result = transcribe_audio_bytes(
            audio_data=audio_data, filename=filename, language=language, model=model
        )

        details = {
            key: value for key, value in result.items() if key != "transcription"
        }

        return result["transcription"], details

    except Exception as error:
        return "", {"success": False, "error": str(error)}


with gr.Blocks(title="VoiceText AI", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🎙️ VoiceText AI
    ### AI-powered Speech-to-Text Transcription

    Upload an audio file or record your voice to convert speech into text.
    """)

    model_input = gr.Radio(
        choices=MODELS, value="indic", label="Choose Transcription Model"
    )

    gr.Markdown("""
    **Whisper:** English speech only. English is selected automatically.

    **Indic-Transcribe:** Supports English, Hindi, Kannada, Malayalam,
    Tamil and Telugu.
    """)

    language_input = gr.Dropdown(
        choices=LANGUAGES,
        value="auto",
        label="Spoken Language (Indic-Transcribe only)",
        interactive=True,
    )

    gr.Markdown("### Provide your audio")

    uploaded_file = gr.File(
        label="Upload Audio",
        file_types=[".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac", ".aac"],
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
        inputs=[uploaded_file, recorded_audio, model_input, language_input],
        outputs=[transcription_output, details_output],
    )


if __name__ == "__main__":
    demo.launch()

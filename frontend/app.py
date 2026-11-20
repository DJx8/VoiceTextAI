import os
import gradio as gr

from backend.transcription import transcribe_audio_bytes

MODELS = [
    ("Whisper - English only (Groq)", "whisper"),
    ("Indic-Transcribe - Multilingual (Bodhan)", "indic"),
]


LANGUAGES = [
    ("Automatic Detection", "auto"),
    ("English", "en"),
    ("Assamese", "as"),
    ("Bengali", "bn"),
    ("Bodo", "brx"),
    ("Dogri", "doi"),
    ("Gujarati", "gu"),
    ("Hindi", "hi"),
    ("Kannada", "kn"),
    ("Kashmiri", "ks"),
    ("Konkani", "kok"),
    ("Maithili", "mai"),
    ("Malayalam", "ml"),
    ("Manipuri", "mni"),
    ("Marathi", "mr"),
    ("Nepali", "ne"),
    ("Odia", "or"),
    ("Punjabi", "pa"),
    ("Sanskrit", "sa"),
    ("Santali", "sat"),
    ("Sindhi", "sd"),
    ("Tamil", "ta"),
    ("Telugu", "te"),
    ("Urdu", "ur"),
    ("Bhojpuri", "bho"),
    ("Bhili", "bhb"),
]


def transcribe_audio(uploaded_file, recorded_audio, model, language):

    audio_path = uploaded_file or recorded_audio

    if audio_path is None:
        return (
            "",
            "",
            {"success": False, "error": "Please upload or record audio."},
        )

    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        filename = os.path.basename(audio_path)

        result = transcribe_audio_bytes(
            audio_data=audio_data,
            filename=filename,
            language=language,
            model=model,
        )

        transcription = result.get("transcription", "")
        translation = result.get(
            "translation",
            "Translation not required. Audio is already in English.",
        )

        details = {
            key: value
            for key, value in result.items()
            if key not in {"transcription", "translation"}
        }

        return transcription, translation, details

    except Exception as error:
        return (
            "",
            "",
            {"success": False, "error": str(error)},
        )


with gr.Blocks(title="VoiceText AI") as demo:

    gr.Markdown("""
    # VoiceText AI

    ### AI-powered Multilingual Speech-to-Text and Translation

    Upload an audio file or record your voice.

    Get the original transcription in the spoken language
    and its English translation.
    """)

    model_input = gr.Radio(
        choices=MODELS,
        value="indic",
        label="Choose Transcription Model",
    )

    gr.Markdown("""
    **Whisper:** English speech transcription using Groq.

    **Indic-Transcribe:** Multilingual speech transcription
    with English translation where supported.

    **Note:** Bhojpuri and Bhili transcription are supported,
    but English translation is unavailable.
    """)

    language_input = gr.Dropdown(
        choices=LANGUAGES,
        value="auto",
        label="Spoken Language (Indic-Transcribe only)",
        interactive=True,
    )

    gr.Markdown("### Provide Your Audio")

    uploaded_file = gr.File(
        label="Upload Audio",
        file_types=[
            ".mp3",
            ".wav",
            ".m4a",
            ".mp4",
            ".webm",
            ".ogg",
            ".flac",
            ".aac",
        ],
        type="filepath",
    )

    recorded_audio = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Or Record Your Voice",
    )

    transcribe_btn = gr.Button(
        "Transcribe Audio",
        variant="primary",
    )

    gr.Markdown("### Original Transcription")

    transcription_output = gr.Textbox(
        label="Transcription in Original Language",
        lines=8,
        interactive=False,
    )

    gr.Markdown("### English Translation")

    translation_output = gr.Textbox(
        label="English Translation",
        lines=8,
        interactive=False,
    )

    details_output = gr.JSON(
        label="Processing Details",
    )

    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[
            uploaded_file,
            recorded_audio,
            model_input,
            language_input,
        ],
        outputs=[
            transcription_output,
            translation_output,
            details_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()

import os
import gradio as gr

from backend.transcription import transcribe_audio_bytes
from backend.bodhan_direct import process_bodhan_direct

# --------------------------------------------------
# MODEL CONFIGURATION
# --------------------------------------------------

MODELS = [
    ("Whisper - English only (Groq)", "whisper"),
    ("Indic-Transcribe - Multilingual (Bodhan)", "indic"),
    ("Bodhan AI - Direct API", "bodhan_direct"),
]


# --------------------------------------------------
# SUPPORTED LANGUAGES
# --------------------------------------------------

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


# --------------------------------------------------
# BODHAN INDIC-SPEAK VOICE MAPPING
# --------------------------------------------------

VOICES = {
    "as": {"Female": ["Prastuti"], "Male": ["Ankur"]},
    "bn": {"Female": ["Ishita"], "Male": ["Sourav"]},
    "brx": {"Female": ["Gwrbw"], "Male": ["Sansuma"]},
    "doi": {"Female": ["Preeti"], "Male": ["Sham"]},
    "gu": {"Female": ["Dhara"], "Male": ["Parth"]},
    "hi": {"Female": ["Kavya", "Suhani"], "Male": ["Amit"]},
    "kn": {"Female": ["Deepika"], "Male": ["Adarsh"]},
    "kok": {"Female": ["Anjali"], "Male": ["Sandeep"]},
    "ks": {"Female": ["Zoon"], "Male": ["Ishfaq"]},
    "mai": {"Female": ["Vaidehi"], "Male": ["Madhukar"]},
    "ml": {"Female": ["Lakshmi"], "Male": ["Kiran"]},
    "mni": {"Female": ["Thoibi"], "Male": ["Chaoba"]},
    "mr": {"Female": ["Anagha"], "Male": ["Chinmay"]},
    "ne": {"Female": ["Srijana"], "Male": ["Sagar"]},
    "or": {"Female": ["Itishree"], "Male": ["Akash"]},
    "pa": {"Female": ["Kaur"], "Male": ["Manpreet"]},
    "sa": {"Female": ["Bharati"], "Male": ["Aryaman"]},
    "sat": {"Female": ["Phulmani"], "Male": ["Sibu"]},
    "sd": {"Female": ["Moomal"], "Male": ["Rano"]},
    "ta": {"Female": ["Anitha"], "Male": ["Arun"]},
    "te": {"Female": ["Sravani"], "Male": ["Vamsi"]},
    "ur": {"Female": ["Saba"], "Male": ["Zaid"]},
}


# --------------------------------------------------
# MODEL UI VISIBILITY
# --------------------------------------------------


def update_model_ui(model):
    is_direct = model == "bodhan_direct"

    return (
        gr.update(visible=is_direct),
        gr.update(visible=is_direct),
        gr.update(visible=is_direct),
    )


# --------------------------------------------------
# MAIN AUDIO PROCESSING FUNCTION
# --------------------------------------------------


def transcribe_audio(
    uploaded_file,
    recorded_audio,
    model,
    language,
    generate_speech,
    tts_language,
    voice_gender,
):

    audio_path = uploaded_file or recorded_audio

    if audio_path is None:
        return (
            "",
            "",
            "",
            None,
            {"success": False, "error": "Please upload or record audio."},
        )

    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        filename = os.path.basename(audio_path)

        # ------------------------------------------
        # BODHAN DIRECT API MODE
        # ------------------------------------------

        if model == "bodhan_direct":

            # Automatically select voice based on
            # target language and selected gender.

            voice_list = VOICES.get(tts_language, {}).get(voice_gender, [])

            if generate_speech and not voice_list:
                raise ValueError(
                    "No voice is available for the selected " "language and gender."
                )

            # Select the first available voice.
            voice = voice_list[0] if voice_list else None

            result = process_bodhan_direct(
                audio_data=audio_data,
                filename=filename,
                spoken_language=language,
                tts_language=tts_language,
                voice=voice,
                generate_speech=generate_speech,
            )

            transcription = result.get("transcription", "")

            translation = result.get("translation", "")

            speech_text = result.get("speech_text", "")

            generated_audio = result.get("audio_path")

            details = {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "transcription",
                    "translation",
                    "speech_text",
                    "audio_path",
                }
            }

            return (
                transcription,
                translation,
                speech_text,
                generated_audio,
                details,
            )

        # ------------------------------------------
        # EXISTING WHISPER AND INDIC MODES
        # ------------------------------------------

        result = transcribe_audio_bytes(
            audio_data=audio_data,
            filename=filename,
            language=language,
            model=model,
        )

        transcription = result.get("transcription", "")

        translation = result.get(
            "translation",
            "Translation not required. " "Audio is already in English.",
        )

        details = {
            key: value
            for key, value in result.items()
            if key
            not in {
                "transcription",
                "translation",
            }
        }

        return (
            transcription,
            translation,
            "",
            None,
            details,
        )

    except Exception as error:

        return (
            "",
            "",
            "",
            None,
            {
                "success": False,
                "error": str(error),
            },
        )


# --------------------------------------------------
# GRADIO INTERFACE
# --------------------------------------------------

with gr.Blocks(title="VoiceText AI") as demo:

    gr.Markdown("""
    # VoiceText AI

    ### AI-powered Multilingual Speech-to-Text and Translation

    Upload an audio file or record your voice.

    Get the original transcription in the spoken language
    and its English translation.
    """)

    # ----------------------------------------------
    # MODEL SELECTION
    # ----------------------------------------------

    model_input = gr.Radio(
        choices=MODELS,
        value="indic",
        label="Choose Transcription Model",
    )

    gr.Markdown("""
    **Whisper:** English speech transcription using Groq.

    **Indic-Transcribe:** Multilingual transcription using
    Bodhan through our Hugging Face Space.

    **Bodhan AI - Direct API:** Direct Bodhan transcription,
    English translation, regional-language translation
    and speech generation.

    **Note:** Bhojpuri and Bhili transcription are supported
    in the existing Indic mode, but English translation
    is unavailable there.
    """)

    # ----------------------------------------------
    # SPOKEN LANGUAGE
    # ----------------------------------------------

    language_input = gr.Dropdown(
        choices=LANGUAGES,
        value="auto",
        label="Spoken Language",
        interactive=True,
    )

    # ----------------------------------------------
    # BODHAN DIRECT API SETTINGS
    # ----------------------------------------------

    with gr.Group(visible=False) as direct_options:

        gr.Markdown("### Bodhan Direct API Settings")

        generate_speech_input = gr.Checkbox(
            value=True,
            label="Generate regional-language speech",
        )

        tts_language_input = gr.Dropdown(
            choices=[(name, code) for name, code in LANGUAGES if code in VOICES],
            value="ml",
            label="Target Language",
            interactive=True,
        )

        gender_input = gr.Dropdown(
            choices=["Female", "Male"],
            value="Female",
            label="Voice Gender",
            interactive=True,
        )

    # ----------------------------------------------
    # AUDIO INPUT
    # ----------------------------------------------

    gr.Markdown("### Provide Your Audio")

    uploaded_file = gr.File(
        label="Upload Audio",
        type="filepath",
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
    )

    recorded_audio = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Or Record Your Voice",
    )

    transcribe_btn = gr.Button(
        "Process Audio",
        variant="primary",
    )

    # ----------------------------------------------
    # TRANSCRIPTION OUTPUT
    # ----------------------------------------------

    transcription_output = gr.Textbox(
        label="Transcription in Original Language",
        lines=5,
        interactive=False,
    )

    translation_output = gr.Textbox(
        label="English Translation",
        lines=5,
        interactive=False,
    )

    # ----------------------------------------------
    # DIRECT API SPEECH OUTPUTS
    # ----------------------------------------------

    speech_text_output = gr.Textbox(
        label="Text Used for Speech Generation",
        lines=4,
        visible=False,
        interactive=False,
    )

    audio_output = gr.Audio(
        label="Generated Regional-Language Speech",
        type="filepath",
        interactive=False,
        visible=False,
    )

    # ----------------------------------------------
    # PROCESSING DETAILS
    # ----------------------------------------------

    details_output = gr.JSON(
        label="Processing Details",
    )

    # ----------------------------------------------
    # MODEL CHANGE EVENT
    # ----------------------------------------------

    model_input.change(
        fn=update_model_ui,
        inputs=model_input,
        outputs=[
            direct_options,
            speech_text_output,
            audio_output,
        ],
    )

    # ----------------------------------------------
    # PROCESS AUDIO EVENT
    # ----------------------------------------------

    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[
            uploaded_file,
            recorded_audio,
            model_input,
            language_input,
            generate_speech_input,
            tts_language_input,
            gender_input,
        ],
        outputs=[
            transcription_output,
            translation_output,
            speech_text_output,
            audio_output,
            details_output,
        ],
    )


# --------------------------------------------------
# LAUNCH APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    demo.launch()

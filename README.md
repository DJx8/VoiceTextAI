# VoiceText AI

### Multilingual Speech-to-Text, English Translation and Speech Generation

VoiceText AI is an AI-powered audio processing application. It accepts uploaded audio or microphone recordings and provides transcription in the spoken language, an English translation where supported, and optional regional-language speech generation.

The Gradio interface offers **three processing modes**:

1. **Whisper – English only (Groq):** English speech transcription using Groq Whisper Large V3.
2. **Indic-Transcribe – Multilingual (Bodhan):** Multilingual transcription and English translation through a private Hugging Face Space.
3. **Bodhan AI – Direct API:** Direct Bodhan API integration for regional transcription, English translation, translation into a selected regional language, and optional text-to-speech (TTS).

**Live application:** https://voicetextai.onrender.com  
**GitHub repository:** https://github.com/DJx8/VoiceTextAI

---

## Features

- Audio upload and browser microphone recording.
- English transcription with Groq Whisper Large V3.
- Multilingual transcription with Bodhan Indic-Transcribe Core.
- A separate direct Bodhan API processing mode.
- Automatic language detection and manual spoken-language selection where supported.
- Original-language transcription in its native script.
- English translation in the Indic and Bodhan Direct modes, where supported by the translation service.
- Optional translation of the English result into a selected regional language.
- Optional regional-language speech generation using Bodhan Indic-Speak.
- Female or male voice selection, with the voice name selected automatically for the chosen language and gender.
- Automatic audio conversion to mono, 16 kHz WAV before transcription.
- Processing details, including audio duration and processing time.
- FastAPI REST API for the existing Whisper and Hugging Face Indic modes.
- Offline automated tests using mocked API responses.

## Processing Modes

| Mode | Service / model | Output |
|---|---|---|
| Whisper – English only | Groq `whisper-large-v3` | English transcription |
| Indic-Transcribe – Multilingual | Private Hugging Face Space using `bodhan-ai/indic-transcribe-core` and its translation pipeline | Original-language transcription and English translation where supported |
| Bodhan AI – Direct API | Bodhan `indic-transcribe`, `indic-translate`, and optionally `indic-speak` | Original-language transcription, English translation, optional regional-language text and generated speech |

### 1. Whisper – English only (Groq)

- Uses Groq's `whisper-large-v3` model.
- The spoken language is fixed to English.
- Returns the English transcription.
- Does not generate a separate English translation because the transcription is already in English.

### 2. Indic-Transcribe – Multilingual (Bodhan)

- Uses the private Hugging Face Space `Deejay888/VoiceText-AI`.
- The Space uses `bodhan-ai/indic-transcribe-core` and its combined transcription-and-translation workflow.
- Returns the original-language transcription and an English translation where supported.
- Supports automatic detection and the language options listed below.

### 3. Bodhan AI – Direct API

This mode calls Bodhan's APIs directly from the application:

1. **Transcription:** Bodhan `indic-transcribe` converts the audio into text in the spoken language.
2. **Regional language to English:** Bodhan `indic-translate` translates the transcription into English.
3. **English to selected regional language (optional):** If speech generation is enabled, the English text is translated into the selected target language.
4. **Text-to-speech (optional):** Bodhan `indic-speak` generates audio from that regional-language text.

In the interface, you can:
- Enable or disable regional-language speech generation.
- Select a target language.
- Select Female or Male voice gender.
- Let the application choose the available voice automatically for that language and gender.

For automatic spoken-language detection, the direct transcription request leaves the language parameter out of the API request. The selected target language for speech generation is a separate setting from the spoken language.

**Note:** The Direct API mode uses Bodhan API credentials and may consume API credits. TTS is optional; transcription and English translation are performed as the main pipeline.

---

## Supported Languages

The transcription interfaces provide the following language options:

| Language | Code |
|---|---|
| Automatic Detection | `auto` |
| English | `en` |
| Assamese | `as` |
| Bengali | `bn` |
| Bodo | `brx` |
| Dogri | `doi` |
| Gujarati | `gu` |
| Hindi | `hi` |
| Kannada | `kn` |
| Kashmiri | `ks` |
| Konkani | `kok` |
| Maithili | `mai` |
| Malayalam | `ml` |
| Manipuri | `mni` |
| Marathi | `mr` |
| Nepali | `ne` |
| Odia | `or` |
| Punjabi | `pa` |
| Sanskrit | `sa` |
| Santali | `sat` |
| Sindhi | `sd` |
| Tamil | `ta` |
| Telugu | `te` |
| Urdu | `ur` |
| Bhojpuri | `bho` |
| Bhili | `bhb` |

**Translation availability:** Transcription and translation are separate capabilities. In the existing Hugging Face Indic mode, Bhojpuri and Bhili transcription are supported, but English translation is unavailable for these two languages. Translation availability in the Direct API mode depends on the Bodhan translation service and its supported language pairs.

### Regional-language speech voices

The Direct API interface currently offers target-language speech generation for languages with configured voices:

Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Konkani, Kashmiri, Maithili, Malayalam, Manipuri, Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu and Urdu.

The application selects the configured voice based on the chosen target language and gender. The voice name is not a separate user setting.

---

## Architecture

```text
                         User
                           |
                           v
                    Gradio Frontend
                  Upload / Microphone
                           |
                           v
                     FastAPI App
                           |
                           v
                     Audio Input
                           |
                           v
                Audio Conversion (FFmpeg)
                    Mono, 16 kHz WAV
                           |
                           v
                    Processing Mode
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     Groq Whisper    Hugging Face       Bodhan Direct
     Large V3        Private Space      API Pipeline
          |                |                |
          v                v                v
     English text    Indic transcription  Bodhan transcription
                     + English translation       |
                                            Regional text
                                                  |
                                                  v
                                           English translation
                                                  |
                                       +----------+----------+
                                       |                     |
                                       v                     v
                                Regional translation   Optional TTS
                                       |                     |
                                       +----------+----------+
                                                  |
                                                  v
                                           Results to User
```

The Gradio interface is mounted inside FastAPI, so the website and REST API run through a single application.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend and REST API |
| Gradio | Web interface |
| Groq API | Whisper inference |
| Hugging Face Spaces | Existing multilingual transcription and translation service |
| `gradio_client` | Communication with the private Hugging Face Space |
| Bodhan API | Direct transcription, translation and text-to-speech |
| FFmpeg | Audio conversion |
| `imageio-ffmpeg` | FFmpeg binary management |
| Uvicorn | ASGI server |
| pytest | Automated testing |
| Git and GitHub | Version control |
| Render | Application deployment |

## Project Structure

```text
VoiceTextAI/
|
|-- backend/
|   |-- __init__.py
|   |-- main.py
|   |-- transcription.py
|   |-- bodhan_direct.py
|
|-- frontend/
|   |-- __init__.py
|   |-- app.py
|
|-- tests/
|   |-- test_api.py
|   |-- test_transcription.py
|   |-- test_bodhan_direct.py
|
|-- .env
|-- .gitignore
|-- requirements.txt
|-- requirements-dev.txt
|-- README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/DJx8/VoiceTextAI.git
cd VoiceTextAI
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

For the application:

```bash
pip install -r requirements.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Add the credentials for the services you intend to use:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token

BODHAN_TRANSCRIBE_KEY=your_bodhan_transcription_key
BODHAN_TRANSLATE_KEY=your_bodhan_translation_key
BODHAN_SPEAK_KEY=your_bodhan_speech_key
```

| Variable | Used for |
|---|---|
| `GROQ_API_KEY` | Whisper mode |
| `HF_TOKEN` | Access to the private Hugging Face Space used by Indic-Transcribe mode |
| `BODHAN_TRANSCRIBE_KEY` | Direct Bodhan transcription |
| `BODHAN_TRANSLATE_KEY` | Direct Bodhan translation |
| `BODHAN_SPEAK_KEY` | Direct Bodhan speech generation |

You only need to configure credentials for the modes you plan to use. The Hugging Face token must have access to the private Space.

**Security:** Never commit `.env` or publish API keys. The `.env` file is excluded through `.gitignore`. For Render, add the required variables in the service's Environment settings rather than uploading the local `.env` file.

### 5. Run the application locally

```bash
uvicorn backend.main:app --reload
```

The application will be available at:

| Service | URL |
|---|---|
| VoiceText AI Website | http://127.0.0.1:8000/ |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

---

## REST API

The FastAPI `/transcribe` endpoint currently exposes the **Whisper** and **Hugging Face Indic** modes. The Bodhan Direct API pipeline is currently available through the Gradio interface.

### Transcription endpoint

```http
POST /transcribe
```

Request format: `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Audio file |
| `model` | String | No | `whisper` or `indic`; default: `indic` |
| `language` | String | No | Language code; default: `auto` |

Supported audio extensions:

- MP3
- WAV
- M4A
- MP4
- WebM
- OGG
- FLAC
- AAC

Whisper always uses English, regardless of the supplied language field.

### Python API Example

Install Requests if needed:

```bash
pip install requests
```

Example using Indic-Transcribe:

```python
import requests

url = "https://voicetextai.onrender.com/transcribe"

with open("sample_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio},
        data={
            "model": "indic",
            "language": "kn"
        },
        timeout=300
    )

response.raise_for_status()
print(response.json())
```

Example using Whisper:

```python
import requests

url = "https://voicetextai.onrender.com/transcribe"

with open("english_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio},
        data={"model": "whisper"},
        timeout=120
    )

response.raise_for_status()
print(response.json())
```

### Health endpoint

```http
GET /health
```

Example response:

```json
{
    "status": "running",
    "application": "VoiceText AI"
}
```

---

## Automated Testing

Run the complete test suite:

```bash
python -m pytest -q
```

The tests use mocked Groq, Hugging Face and Bodhan API responses. They do not make real inference requests or consume API credits.

Coverage includes:

- Audio and model validation.
- Language validation.
- Whisper transcription.
- Hugging Face Indic transcription and translation.
- Direct Bodhan transcription, translation and TTS request handling.
- Translation and optional speech-generation error handling.
- FastAPI health endpoint.
- API request validation and error responses.

**Latest local verification:** 23 tests passed.

---

## Deployment on Render

The application is deployed on Render.

**Build command:**

```bash
pip install -r requirements.txt
```

**Start command:**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Add the environment variables required by the modes you want to enable in the Render service's **Environment** settings:

- `GROQ_API_KEY`
- `HF_TOKEN`
- `BODHAN_TRANSCRIBE_KEY`
- `BODHAN_TRANSLATE_KEY`
- `BODHAN_SPEAK_KEY`

The Hugging Face Space must be accessible using the configured token. Do not add secret values to the repository or README.

**Live application:** https://voicetextai.onrender.com

---

## Cost Considerations

VoiceText AI integrates third-party inference APIs and hosting services. Usage charges, free-tier limits, quotas and availability depend on each provider and may change.

- Whisper mode uses the Groq API.
- Indic-Transcribe mode uses the configured Hugging Face Space.
- Bodhan Direct mode can make separate transcription, translation and TTS API requests.
- Disabling speech generation skips the final regional translation-for-speech and TTS stages.

Check each provider's current pricing and usage limits before running large volumes of audio.

## Future Improvements

- [ ] Add transcription download as TXT.
- [ ] Add transcription history.
- [ ] Add timestamps and subtitle generation.
- [ ] Improve long-audio processing through chunking.
- [ ] Benchmark transcription and translation quality across supported languages.
- [ ] Improve translation coverage and language-pair validation.
- [ ] Add additional Indian language support.
- [ ] Add the Bodhan Direct pipeline to the public REST API.
- [ ] Improve error handling and monitoring.

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, AI and a passion for learning.**

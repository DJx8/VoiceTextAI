# VoiceText AI

### Multilingual Speech-to-Text and English Translation

VoiceText AI is an AI-powered speech processing application that converts audio into text in its original language and provides a separate English translation where supported.

It offers two transcription engines:

- **Groq Whisper Large V3** for English speech transcription.
- **Bodhan Indic-Transcribe Core** through a private Hugging Face Space for multilingual transcription and translation.

The application provides a Gradio web interface, a FastAPI REST API, audio file uploads, and microphone recording.

**Live application:** https://voicetextai.onrender.com  
**GitHub repository:** https://github.com/DJx8/VoiceTextAI

## Features

- English speech transcription using Groq Whisper Large V3.
- Multilingual speech transcription using Bodhan Indic-Transcribe Core.
- Original-language transcription in its native script.
- Separate English translation where supported.
- Automatic language detection.
- Manual language selection.
- Audio file upload.
- Browser microphone recording.
- Automatic audio conversion to mono, 16 kHz WAV.
- REST API integration.
- Processing time and audio duration metadata.
- Automated offline tests using mocked API responses.

## Supported Languages

The Indic transcription interface currently provides 26 language options, including automatic detection.

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

**Translation availability:** Transcription and translation are separate capabilities. Bhojpuri and Bhili transcription are supported, but English translation is unavailable for these two languages. For other languages, translation availability depends on the translation model.

## Transcription Models

| Feature | Whisper (Groq) | Indic-Transcribe Core |
|---|---|---|
| English transcription | Yes | Yes |
| Regional language transcription | No | Supported language options |
| Automatic language detection | No | Yes |
| Manual language selection | English only | Yes |
| Separate English translation | Not required | Where supported |

### Whisper

Uses `whisper-large-v3` through the Groq API. The language is fixed to English.

### Indic-Transcribe

Uses `bodhan-ai/indic-transcribe-core` through the private Hugging Face Space:

`Deejay888/VoiceText-AI`

The Space provides a combined transcription and translation endpoint. The application receives:

1. Original-language transcription.
2. English translation or an unavailable message.
3. Detected language.

## Architecture

```text
                   User
                     |
                     v
              Gradio Frontend
            Upload / Microphone
                     |
                     v
               FastAPI Backend
                     |
                     v
               Audio Conversion
               Mono, 16 kHz WAV
                     |
                     v
              Transcription Router
                     |
               +-----+------+
               |            |
               v            v
          Groq Whisper   Hugging Face
          Large V3       Private Space
                             |
                      Indic Transcription
                      + English Translation
                             |
               +-------------+
               |
               v
             API Response
               |
               v
        Original Transcription
        English Translation
               |
               v
              User
```

The Gradio interface is mounted inside FastAPI, allowing the website and REST API to run through a single application.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend and REST API |
| Gradio | Web interface |
| Groq API | Whisper inference |
| Hugging Face Spaces | Indic transcription and translation service |
| `gradio_client` | Communication with the Hugging Face Space |
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
|
|-- frontend/
|   |-- __init__.py
|   |-- app.py
|
|-- tests/
|   |-- test_api.py
|   |-- test_transcription.py
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

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it using Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

Install application dependencies:

```bash
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
```

Required credentials:

- Groq API key: https://console.groq.com/keys
- Hugging Face token: https://huggingface.co/settings/tokens

The Hugging Face token must have access to the private Space and any gated model repository required by it.

Never commit your `.env` file or expose your API keys publicly.

### 5. Run the application

```bash
uvicorn backend.main:app --reload
```

The application will be available at:

| Service | URL |
|---|---|
| VoiceText AI Website | http://127.0.0.1:8000/ |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## REST API

VoiceText AI provides a REST API for external applications.

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

Install the Requests library if needed:

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

### Example Indic API Response

```json
{
    "success": true,
    "filename": "kannada.wav",
    "selected_model": "indic",
    "model": "indic-transcribe-core",
    "language": "kn",
    "requested_language": "kn",
    "detected_language": "Kannada",
    "duration_seconds": 12.5,
    "processing_time_seconds": 2.1,
    "api_request_time_seconds": 1.8,
    "transcription": "ನಮಸ್ಕಾರ",
    "translation": "Hello"
}
```

The response values above are illustrative.

The Indic response includes both transcription and translation. The Whisper response includes transcription without a separate translation field.

### Health Endpoint

```http
GET /health
```

Example:

```json
{
    "status": "running",
    "application": "VoiceText AI"
}
```

## Automated Testing

The project includes offline automated tests.

Run all tests:

```bash
python -m pytest -q
```

The tests use mocked Groq and Hugging Face responses. They do not make real inference requests or consume API credits.

Current test coverage includes:

- Audio and model validation.
- Language validation.
- Whisper transcription.
- Indic transcription and translation.
- Translation fallback.
- Service error handling.
- FastAPI health endpoint.
- API request validation.
- API error responses.

## Deployment

The application is deployed using Render.

**Build command:**

```bash
pip install -r requirements.txt
```

**Start command:**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Configure these environment variables in Render:

```text
GROQ_API_KEY
HF_TOKEN
```

The Hugging Face Space must be accessible using the configured token.

## Cost Considerations

The project is designed to use free-tier services without requiring paid infrastructure.

However, API availability, usage limits, free-tier quotas and hosting restrictions depend on the respective providers. Free access is not guaranteed to be unlimited.

## Future Improvements

- [ ] Download transcription as TXT.
- [ ] Add transcription history.
- [ ] Add timestamps and subtitle generation.
- [ ] Improve long-audio processing through chunking.
- [ ] Verify translation coverage across all supported languages.
- [ ] Improve transcription accuracy through benchmarking.
- [ ] Add additional Indian language support.
- [ ] Improve error handling and monitoring.

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, AI and a passion for learning.**
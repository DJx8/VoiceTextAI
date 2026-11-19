# VoiceText AI

### AI-Powered Speech-to-Text Transcription

VoiceText AI is a web-based speech recognition application that converts spoken audio into written text. It provides two transcription engines through one interface:

- **Groq Whisper Large V3** for English transcription.
- **AI4Bharat Bodhan Indic-Transcribe Core** for multilingual transcription, accessed through a private Hugging Face Space.

Users can upload audio files or record their voice through a microphone. The application also provides a REST API for integration with external applications.

**Live application:** https://voicetextai.onrender.com  
**GitHub repository:** https://github.com/DJx8/VoiceTextAI

## Features

- **Two transcription engines:** Switch between Whisper and Indic-Transcribe.
- **English transcription:** Groq Whisper Large V3.
- **Multilingual transcription:** Indic-Transcribe Core through a private Hugging Face Space.
- **Six languages exposed through VoiceText AI:** English, Hindi, Kannada, Malayalam, Tamil and Telugu.
- **Automatic language detection** and manual language selection for Indic transcription.
- **Audio upload:** MP3, WAV, M4A, MP4, WebM, OGG, FLAC and AAC.
- **Microphone recording:** Record speech directly from the browser.
- **Automatic audio conversion:** Input audio is converted to mono, 16 kHz WAV before transcription.
- **REST API:** Use transcription from external applications.
- **Transcription metadata:** View the selected model, requested language, audio duration and processing time.

## Transcription models

| Feature | Whisper (Groq) | Indic-Transcribe Core |
|---|---|---|
| English | Yes | Yes |
| Hindi | No | Yes |
| Kannada | No | Yes |
| Malayalam | No | Yes |
| Tamil | No | Yes |
| Telugu | No | Yes |
| Automatic language detection | Not used | Supported |
| Manual language selection | Fixed to English | Supported |

**Whisper** uses `whisper-large-v3` through the Groq API. English is selected for transcription.

**Indic-Transcribe Core** uses the `bodhan-ai/indic-transcribe-core` model. The model runs in a private Hugging Face Space, and the VoiceText AI backend calls that Space using the Gradio Client and a Hugging Face access token.

The underlying model supports additional languages, but the current VoiceText AI API and frontend expose the six languages listed above.

## Architecture

```text
                         User
                           |
                           v
                  VoiceText AI Website
                        Gradio
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
                      /         \
                     /           \
                    v             v
             Groq Whisper     Hugging Face
              Large V3        Private Space
                                  |
                                  v
                         Indic-Transcribe Core
                      (Bodhan AI model, ZeroGPU)
                    \             /
                     \           /
                      v         v
                    Transcribed Text
                           |
                           v
                          User
```

The Gradio frontend is mounted inside FastAPI, allowing the website and REST API to run through a single application. Audio conversion takes place in the backend. Indic inference is handled by the private Hugging Face Space.

## Tech stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend and REST API |
| Gradio | Web interface |
| Groq API | Whisper inference |
| Hugging Face Spaces | Hosting the private Indic transcription service |
| Gradio Client | Calling the private Space from the backend |
| Hugging Face Hub | Model access and authentication |
| FFmpeg | Audio conversion |
| imageio-ffmpeg | FFmpeg binary management |
| Uvicorn | ASGI server |
| Git & GitHub | Version control |
| Render | Application deployment |

## Project structure

```text
VoiceTextAI/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── transcription.py
│
├── frontend/
│   ├── __init__.py
│   └── app.py
│
├── tests/
│   ├── test_bodhan_transcribe.py
│   └── test_bodhan_six_languages.py
│
├── sample_audio/       # Local test files; not committed
├── .env                # API keys and tokens; not committed
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and setup

### 1. Clone the repository

```bash
git clone https://github.com/DJx8/VoiceTextAI.git
cd VoiceTextAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_read_token
```

- Get a Groq API key: https://console.groq.com/keys
- Create a Hugging Face access token: https://huggingface.co/settings/tokens

The Hugging Face token must have permission to access your private VoiceText AI Space and the gated model repository. Never commit the `.env` file or expose API keys and tokens publicly.

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

VoiceText AI exposes a transcription endpoint for external applications.

**Endpoint**

```http
POST /transcribe
```

**Request format:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Audio file |
| `model` | String | No | `whisper` or `indic`; defaults to `indic` |
| `language` | String | No | Language code; defaults to `auto` |

Supported Indic language codes:

| Language | Code |
|---|---|
| Automatic detection | `auto` |
| English | `en` |
| Hindi | `hi` |
| Kannada | `kn` |
| Malayalam | `ml` |
| Tamil | `ta` |
| Telugu | `te` |

Whisper uses English (`en`) for transcription, regardless of the language field.

### Python API example

Install Requests if needed:

```bash
pip install requests
```

```python
import requests

url = "https://voicetextai.onrender.com/transcribe"

with open("sample_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio},
        data={
            "model": "indic",
            "language": "auto"
        },
        timeout=300
    )

response.raise_for_status()
print(response.json())
```

### Use Whisper

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

### Example response

```json
{
    "success": true,
    "filename": "sample_audio.wav",
    "selected_model": "indic",
    "model": "indic-transcribe-core",
    "language": "auto",
    "requested_language": "auto",
    "duration_seconds": 12.5,
    "processing_time_seconds": 10.2,
    "api_request_time_seconds": 8.9,
    "transcription": "Example transcribed text."
}
```

The `language` field represents the requested language setting. In automatic mode, the API response does not currently expose a separately detected language label. Processing times vary with audio length, model queueing and provider availability.

## Deployment

The application is deployed as a single web service on Render. Indic transcription is handled separately by a private Hugging Face Space.

**Render build command**

```bash
pip install -r requirements.txt
```

**Render start command**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Configure these environment variables in the Render dashboard:

```text
GROQ_API_KEY
HF_TOKEN
```

Keep credentials in the hosting provider's environment settings, not in source code or GitHub.

## Cost and usage notes

VoiceText AI is designed to use free-tier services where available. It does not guarantee unlimited or permanently free usage.

- Groq API usage is subject to Groq's current limits and policies.
- Hugging Face ZeroGPU has daily usage quotas and availability limits. Requests may wait for GPU allocation, and inactive Spaces may need to start again.
- Render free-tier availability and limits may change.

The Indic model is provided by Bodhan AI. Its model card and license terms govern use, including use through hosted services. Obtain any required written permission from Bodhan AI before offering the model through a public hosted API.

## Future improvements

- [ ] Add transcription download as TXT.
- [ ] Add transcription history.
- [ ] Add timestamps and subtitle generation.
- [ ] Improve long-audio handling through chunking.
- [ ] Expand the languages exposed by the VoiceText AI API.
- [ ] Improve error handling and API validation.
- [ ] Add performance and accuracy benchmarks.

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, AI and a passion for learning.**

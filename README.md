#  VoiceText AI

### AI-Powered Speech-to-Text Transcription

VoiceText AI is a web-based speech recognition application that converts spoken audio into written text. It provides two transcription engines through a single interface: **Groq Whisper Large V3** for English transcription and **AI4Bharat Bodhan Indic-Transcribe** for multilingual transcription.

Users can upload audio files or record their voice through a microphone. The application also provides a REST API for integration with external applications.

## ✨ Features

- **Two transcription engines:** Switch between Whisper and Indic-Transcribe.
- **English transcription:** Groq Whisper Large V3, with English selected as the fixed language.
- **Multilingual transcription:** Indic-Transcribe supports English, Hindi, Kannada, Malayalam, Tamil and Telugu.
- **Automatic language detection:** Available with Indic-Transcribe.
- **Manual language selection:** Choose the spoken language when using Indic-Transcribe.
- **Audio upload:** Supports MP3, WAV, M4A, MP4, WebM, OGG, FLAC and AAC inputs.
- **Microphone recording:** Record speech directly from the browser.
- **Automatic audio conversion:** Audio is converted to mono, 16 kHz WAV before transcription.
- **REST API:** Integrate transcription into other applications.
- **Transcription metadata:** View the selected model, requested language, audio duration and processing time.

##  Transcription Models

| Feature | Whisper (Groq) | Indic-Transcribe (Bodhan) |
|---|---|---|
| English | Yes | Yes |
| Hindi | No | Yes |
| Kannada | No | Yes |
| Malayalam | No | Yes |
| Tamil | No | Yes |
| Telugu | No | Yes |
| Automatic language detection | Not used | Supported |
| Manual language selection | Fixed to English | Supported |

**Whisper:** Uses `whisper-large-v3` through the Groq API. English is explicitly selected for transcription.

**Indic-Transcribe:** Uses `indic-transcribe` through the Bodhan API. It supports automatic language detection and manual selection for the six supported languages.

##  Architecture

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
                      |
              +-------+-------+
              |               |
              v               v
        Groq Whisper      Bodhan API
        Large V3          Indic-Transcribe
              |               |
              +-------+-------+
                      |
                      v
              Transcribed Text
                      |
                      v
                    User
```

The Gradio frontend is mounted inside FastAPI, allowing the website and REST API to run through a single application.

##  Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend and REST API |
| Gradio | Web interface |
| Groq API | Whisper inference |
| Bodhan API | Indic-Transcribe inference |
| OpenAI Python SDK | Bodhan API communication |
| FFmpeg | Audio conversion |
| imageio-ffmpeg | FFmpeg binary management |
| Uvicorn | ASGI server |
| Git & GitHub | Version control |
| Render | Application deployment |

##  Project Structure

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
├── .env                # API keys; not committed
├── .gitignore
├── requirements.txt
└── README.md
```

##  Installation and Setup

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

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
BODHAN_API_KEY=your_bodhan_api_key
```

Get your API keys:

- Groq: https://console.groq.com/keys
- Bodhan: https://console.bodhan.ai/

**Important:** Never commit your `.env` file or expose your API keys publicly.

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

## 🔌 REST API

VoiceText AI exposes a transcription endpoint for external applications.

**Endpoint:**

```http
POST /transcribe
```

**Request format:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | Audio file |
| `model` | String | No | `whisper` or `indic`; defaults to `indic` |
| `language` | String | No | Language code; defaults to `auto` |

Supported language codes for Indic-Transcribe:

| Language | Code |
|---|---|
| Automatic Detection | `auto` |
| English | `en` |
| Hindi | `hi` |
| Kannada | `kn` |
| Malayalam | `ml` |
| Tamil | `ta` |
| Telugu | `te` |

Whisper always uses English (`en`), regardless of the language field.

### Python API example

```python
import requests

url = "http://127.0.0.1:8000/transcribe"

with open("sample_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio},
        data={
            "model": "indic",
            "language": "auto"
        }
    )

print(response.json())
```

### Use Whisper

```python
import requests

url = "http://127.0.0.1:8000/transcribe"

with open("english_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio},
        data={"model": "whisper"}
    )

print(response.json())
```

### Example response

```json
{
    "success": true,
    "filename": "sample_audio.wav",
    "selected_model": "indic",
    "model": "indic-transcribe",
    "language": "auto",
    "requested_language": "auto",
    "duration_seconds": 12.5,
    "processing_time_seconds": 1.2,
    "api_request_time_seconds": 0.9,
    "transcription": "Example transcribed text."
}
```

The `language` field represents the requested language setting. In automatic mode, the API response does not currently expose a separately detected language label.

## ☁️ Deployment

The application is designed to run as a single web service on Render.

**Render configuration:**

- **Build Command:**

```bash
pip install -r requirements.txt
```

- **Start Command:**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment variables:**

```text
GROQ_API_KEY
BODHAN_API_KEY
```

Add the actual API keys through the Render dashboard. Do not place them in source code or GitHub.

##  Cost

VoiceText AI is designed around a ₹0 development and deployment budget.

It uses free-tier hosting and API access where available. However, free-tier limits, API credits, usage charges and service availability depend on the providers. API usage is not guaranteed to be unlimited or permanently free.

##  Future Improvements

- [ ] Add transcription download as TXT.
- [ ] Add transcription history.
- [ ] Add timestamps and subtitle generation.
- [ ] Improve long-audio handling through chunking.
- [ ] Expand Indian language support.
- [ ] Improve error handling and API validation.
- [ ] Add performance and accuracy benchmarks.


⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, AI and a passion for learning.**
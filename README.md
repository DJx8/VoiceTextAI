# 🎙️ VoiceText AI
### AI-Powered Speech-to-Text Transcription

VoiceText AI is a web-based speech recognition application that converts spoken audio into written text using **OpenAI Whisper Large V3**, accessed through the Groq API.

It provides an easy-to-use interface for uploading audio files or recording voice directly through a microphone. It also exposes a REST API that other applications can use for speech transcription.

## ✨ Features

- **Audio Upload:** Upload audio files in formats such as MP3, WAV, M4A, MP4, WebM and more.
- **Live Microphone Recording:** Record audio directly from your browser.
- **AI Transcription:** Convert speech into text using Whisper Large V3.
- **Language Detection:** Automatically identify the spoken language.
- **Transcription Metadata:** View detected language, audio duration, model and processing time.
- **REST API:** Use the transcription service from external applications.
- **Web Interface:** Simple and interactive interface built with Gradio.
- **Free-Tier Deployment:** Designed to run using free hosting and API tiers, subject to their usage limits.

## Architecture

```text
             User
               |
               v
       VoiceText AI Website
             (Gradio)
               |
               v
        FastAPI Backend
               |
               v
           Groq API
               |
               v
       Whisper Large V3
               |
               v
       Transcribed Text
               |
               v
          User Output
```

The Gradio frontend is mounted inside FastAPI, allowing the website and REST API to run through a single application.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend and REST API |
| Gradio | Web interface |
| Groq API | Model inference |
| Whisper Large V3 | Speech recognition |
| Uvicorn | ASGI server |
| Git & GitHub | Version control |
| Render | Application deployment |

## 📁 Project Structure

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
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/VoiceTextAI.git
cd VoiceTextAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
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

### 4. Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get your API key from:

https://console.groq.com/keys

**Important:** Never upload your `.env` file or expose your API key publicly.

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

VoiceText AI exposes a transcription endpoint that can be integrated into external applications.

**Endpoint:**

```http
POST /transcribe
```

**Request:**

Send an audio file using `multipart/form-data` with the field name `file`.

Example using Python:

```python
import requests

url = "http://127.0.0.1:8000/transcribe"

with open("sample_audio.wav", "rb") as audio:
    response = requests.post(
        url,
        files={"file": audio}
    )

print(response.json())
```

**Example Response:**

```json
{
    "success": true,
    "filename": "sample_audio.wav",
    "model": "whisper-large-v3",
    "language": "English",
    "duration_seconds": 12.5,
    "processing_time_seconds": 0.85,
    "transcription": "Hello, welcome to VoiceText AI."
}
```

## Deployment

The application is designed to be deployed as a single web service using Render.

Deployment configuration:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variable:** `GROQ_API_KEY`

The API key must be configured through the hosting platform's environment variables.

## Model Information

**Model:** Whisper Large V3

**Inference Provider:** Groq

Whisper is a multilingual automatic speech recognition model capable of recognizing speech in multiple languages.

The initial development and testing focused on English speech. Additional language testing and improvements are planned.

## Future Improvements

- [ ] Add language selection.
- [ ] Improve transcription support for Indian languages.
- [ ] Add TXT transcription downloads.
- [ ] Add support for additional audio formats.
- [ ] Improve error handling and input validation.
- [ ] Explore transcription history.
- [ ] Add timestamp-based transcription.

## Cost

This project is designed with a ₹0 development and deployment budget.

It uses free-tier services where available. Actual availability and usage are subject to Groq API limits and hosting provider restrictions.

## Author

**Dhananjay A V**

B.Tech – Artificial Intelligence and Data Science

- GitHub: https://github.com/DJx8
- LinkedIn: https://linkedin.com/in/dhananjay-av

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, AI and a passion for learning.**

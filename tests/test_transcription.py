import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq, APIError, RateLimitError, AuthenticationError

# --------------------------------------------------
# 1. Load project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")


# --------------------------------------------------
# 2. Configuration
# --------------------------------------------------

MODEL = "whisper-large-v3"

AUDIO_FILE = PROJECT_ROOT / "sample_audio" / "sample_english.mp4"

client = Groq(api_key=API_KEY)


# --------------------------------------------------
# 3. Validate audio file
# --------------------------------------------------

if not AUDIO_FILE.exists():
    raise FileNotFoundError(f"Audio file not found: {AUDIO_FILE}")

file_size_mb = AUDIO_FILE.stat().st_size / (1024 * 1024)

print("=" * 55)
print("           VOICETEXT AI - FIRST TEST")
print("=" * 55)

print(f"Audio file : {AUDIO_FILE.name}")
print(f"File size  : {file_size_mb:.2f} MB")
print(f"Model      : {MODEL}")


# --------------------------------------------------
# 4. Send audio to Groq Whisper API
# --------------------------------------------------

print("\nSending audio to GroqCloud...")
print("Please wait...\n")

start_time = time.perf_counter()

try:
    with open(AUDIO_FILE, "rb") as audio:
        transcription = client.audio.transcriptions.create(
            file=(AUDIO_FILE.name, audio.read()),
            model=MODEL,
            language="en",
            response_format="verbose_json",
            temperature=0.0,
        )

    processing_time = time.perf_counter() - start_time

    # --------------------------------------------------
    # 5. Extract transcription results
    # --------------------------------------------------

    result = {
        "model": MODEL,
        "text": transcription.text,
        "language": getattr(transcription, "language", "Not available"),
        "audio_duration_seconds": getattr(transcription, "duration", None),
        "processing_time_seconds": round(processing_time, 3),
    }

    # --------------------------------------------------
    # 6. Display results
    # --------------------------------------------------

    print("=" * 55)
    print("             TRANSCRIPTION RESULT")
    print("=" * 55)

    print("\nTranscribed Text:\n")
    print(result["text"])

    print("\n" + "-" * 55)
    print("TRANSCRIPTION DETAILS")
    print("-" * 55)

    print(f"Model             : {result['model']}")
    print(f"Detected language : {result['language']}")
    print(f"Audio duration    : {result['audio_duration_seconds']} seconds")
    print(f"Processing time   : {result['processing_time_seconds']} seconds")

    # --------------------------------------------------
    # 7. Save output as JSON
    # --------------------------------------------------

    output_file = PROJECT_ROOT / "tests" / "transcription_result.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"\nResult saved to: {output_file}")

    print("\nFirst transcription completed successfully!")

except AuthenticationError:
    print("Authentication failed. Check your Groq API key.")

except RateLimitError as error:
    print(f"Groq rate limit reached: {error}")

except APIError as error:
    print(f"Groq API error: {error}")

except Exception as error:
    print(f"Unexpected error: {type(error).__name__}: {error}")

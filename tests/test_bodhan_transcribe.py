import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Project root
ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

api_key = os.getenv("BODHAN_API_KEY")

if not api_key:
    raise RuntimeError("BODHAN_API_KEY not found in .env")

client = OpenAI(base_url="https://api.bodhan.ai/v1", api_key=api_key)

TESTS = [
    {
        "language": "Kannada",
        "code": "kn",
        "file": ROOT / "sample_audio" / "kannada.wav",
    },
    {
        "language": "Malayalam",
        "code": "ml",
        "file": ROOT / "sample_audio" / "malayalam.wav",
    },
]

for test in TESTS:

    print("\n" + "=" * 55)
    print(f"Testing: {test['language']}")
    print("=" * 55)

    audio_path = test["file"]

    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        continue

    start = time.perf_counter()

    try:
        with open(audio_path, "rb") as audio:

            result = client.audio.transcriptions.create(
                model="indic-transcribe", file=audio, language=test["code"]
            )

        elapsed = time.perf_counter() - start

        print("Language:", test["language"])
        print("Model: indic-transcribe")
        print("Processing time:", round(elapsed, 3), "seconds")
        print("\nTRANSCRIPTION:")
        print(result.text)

    except Exception as error:
        print("ERROR:", str(error))

print("\nAll tests completed.")

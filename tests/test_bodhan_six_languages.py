import os
import time
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "sample_audio"

load_dotenv(ROOT / ".env")

api_key = os.getenv("BODHAN_API_KEY")

if not api_key:
    raise RuntimeError("BODHAN_API_KEY missing from .env")

client = OpenAI(base_url="https://api.bodhan.ai/v1", api_key=api_key)

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

TESTS = [
    ("English", "en", "english.wav"),
    ("Hindi", "hi", "hindi.wav"),
    ("Kannada", "kn", "kannada.wav"),
    ("Malayalam", "ml", "malayalam.wav"),
    ("Tamil", "ta", "tamil.wav"),
    ("Telugu", "te", "telugu.wav"),
]


def convert_to_wav(input_path, output_path):

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)


results = []

with tempfile.TemporaryDirectory() as temp_dir:

    for language, code, filename in TESTS:

        print("\n" + "=" * 55)
        print(f"Testing {language}")
        print("=" * 55)

        input_path = AUDIO_DIR / filename

        if not input_path.exists():
            print(f"SKIPPED: Missing {filename}")
            continue

        wav_path = Path(temp_dir) / f"{code}.wav"

        try:
            # Convert audio to standard WAV
            convert_to_wav(input_path, wav_path)

            start = time.perf_counter()

            with open(wav_path, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="indic-transcribe", file=audio, language=code
                )

            elapsed = time.perf_counter() - start

            print("Status: SUCCESS")
            print("Language:", language)
            print("Time:", round(elapsed, 2), "seconds")
            print("Transcription:")
            print(response.text)

            results.append((language, "SUCCESS", round(elapsed, 2)))

        except Exception as error:
            print("Status: FAILED")
            print("Error:", str(error))

            results.append((language, "FAILED", 0))

print("\n\nFINAL RESULTS")
print("-" * 45)

for language, status, elapsed in results:
    print(f"{language:12} | {status:10} | {elapsed}s")

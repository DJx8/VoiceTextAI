import json
import re
import time
from pathlib import Path

from datasets import load_dataset, Audio
from dotenv import load_dotenv
from groq import Groq
from jiwer import wer, cer, process_words

# ---------------- CONFIGURATION ----------------

SAMPLE_LIMIT = 50
MODEL = "whisper-large-v3"

OUTPUT_FILE = Path("tests/benchmark_results_svarah.json")

load_dotenv()
client = Groq()

# ---------------- TEXT NORMALIZATION ----------------


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------- SAVE RESULTS ----------------


def save_results(results):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


# ---------------- LOAD PREVIOUS RESULTS ----------------

if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        saved_results = json.load(f)
else:
    saved_results = []

results_by_index = {item["sample_index"]: item for item in saved_results}

completed = {
    index
    for index, item in results_by_index.items()
    if "prediction" in item and not item.get("error")
}

print(f"Already completed: {len(completed)} samples")

# ---------------- LOAD SVARAH ----------------

print("\nLoading Svarah dataset...")

dataset = load_dataset("ai4bharat/Svarah", split="test", streaming=True, token=True)

dataset = dataset.cast_column("audio_filepath", Audio(decode=False))

print("\nStarting Whisper benchmark...")
print(f"Model: {MODEL}")
print(f"Target samples: {SAMPLE_LIMIT}")

# ---------------- TRANSCRIPTION ----------------

try:
    for index, sample in enumerate(dataset):

        if index >= SAMPLE_LIMIT:
            break

        if index in completed:
            print(f"\nSkipping completed sample {index + 1}")
            continue

        audio = sample["audio_filepath"]
        audio_bytes = audio.get("bytes")

        if not audio_bytes:
            print(f"Missing audio bytes for sample {index + 1}")
            continue

        reference = sample["text"]

        print("\n" + "=" * 55)
        print(f"Sample: {index + 1}/{SAMPLE_LIMIT}")
        print(f"State: {sample['native_place_state']}")
        print(f"Native language: {sample['primary_language']}")
        print(f"Duration: {sample['duration']:.2f} seconds")

        try:
            start_time = time.perf_counter()

            response = client.audio.transcriptions.create(
                file=(f"svarah_{index + 1:04d}.wav", audio_bytes),
                model=MODEL,
                language="en",
                response_format="verbose_json",
                temperature=0.0,
            )

            processing_time = time.perf_counter() - start_time

            prediction = response.text

            result = {
                "sample_index": index,
                "model": MODEL,
                "reference": reference,
                "prediction": prediction,
                "duration_seconds": sample["duration"],
                "processing_time_seconds": round(processing_time, 4),
                "gender": sample["gender"],
                "age_group": sample["age-group"],
                "native_language": sample["primary_language"],
                "state": sample["native_place_state"],
                "district": sample["native_place_district"],
            }

            results_by_index[index] = result
            save_results(
                sorted(results_by_index.values(), key=lambda x: x["sample_index"])
            )

            print("REFERENCE :", reference)
            print("PREDICTION:", prediction)
            print(f"API time  : {processing_time:.3f} seconds")

        except Exception as e:
            print(f"\nAPI ERROR: {e}")

            results_by_index[index] = {"sample_index": index, "error": str(e)}

            save_results(
                sorted(results_by_index.values(), key=lambda x: x["sample_index"])
            )

            print("Progress saved. Stopping benchmark.")
            break

except Exception as e:
    print(f"\nDATASET STREAMING ERROR: {e}")
    print("Previously completed results have been saved.")

# ---------------- EVALUATION ----------------

successful_results = [
    item
    for item in results_by_index.values()
    if "prediction" in item and not item.get("error")
]

successful_results.sort(key=lambda x: x["sample_index"])

if successful_results:

    references = [normalize_text(item["reference"]) for item in successful_results]

    predictions = [normalize_text(item["prediction"]) for item in successful_results]

    word_stats = process_words(references, predictions)

    total_duration = sum(item["duration_seconds"] for item in successful_results)

    total_api_time = sum(item["processing_time_seconds"] for item in successful_results)

    print("\n" + "=" * 55)
    print("SVARAH BENCHMARK SUMMARY")
    print("=" * 55)

    print(f"Dataset samples completed: {len(successful_results)}")
    print(f"Total audio duration: {total_duration:.2f} seconds")

    print(f"Total API time: {total_api_time:.2f} seconds")
    print(
        f"Average API time: " f"{total_api_time / len(successful_results):.3f} seconds"
    )

    print(f"\nWER: {wer(references, predictions) * 100:.2f}%")
    print(f"CER: {cer(references, predictions) * 100:.2f}%")

    print(f"\nCorrect words: {word_stats.hits}")
    print(f"Substitutions: {word_stats.substitutions}")
    print(f"Deletions: {word_stats.deletions}")
    print(f"Insertions: {word_stats.insertions}")

    print("\nResults saved to:", OUTPUT_FILE)

else:
    print("\nNo successful transcriptions yet.")

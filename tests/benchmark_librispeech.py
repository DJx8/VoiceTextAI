import json
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from jiwer import process_words, process_characters

# --------------------------------------------------
# 1. PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_DIR / "LibriSpeech" / "test-clean"

RESULTS_FILE = PROJECT_DIR / "tests" / "benchmark_results.json"

MODEL = "whisper-large-v3"

SPEAKERS = {
    "6930": "75918",
    "1320": "122617",
    "5639": "40744",
    "260": "123440",
    "7729": "102255",
}

load_dotenv(PROJECT_DIR / ".env")
client = Groq()


# --------------------------------------------------
# 2. TEXT NORMALIZATION
# --------------------------------------------------


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# --------------------------------------------------
# 3. LOAD REFERENCE TRANSCRIPTS
# --------------------------------------------------


def load_samples():
    samples = []

    for speaker_id, chapter_id in SPEAKERS.items():

        transcript_file = (
            DATASET_DIR
            / speaker_id
            / chapter_id
            / f"{speaker_id}-{chapter_id}.trans.txt"
        )

        with open(transcript_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Select the first four recordings from each speaker.
        for line in lines[:4]:
            audio_id, reference = line.strip().split(" ", 1)

            audio_file = DATASET_DIR / speaker_id / chapter_id / f"{audio_id}.flac"

            if not audio_file.exists():
                raise FileNotFoundError(audio_file)

            samples.append(
                {
                    "audio_id": audio_id,
                    "speaker_id": speaker_id,
                    "audio_path": str(audio_file),
                    "reference": reference,
                }
            )

    return samples


# --------------------------------------------------
# 4. SAVE RESULTS AFTER EACH RECORDING
# --------------------------------------------------


def save_results(results):
    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


# --------------------------------------------------
# 5. TRANSCRIBE RECORDINGS
# --------------------------------------------------


def transcribe_samples(samples):

    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", encoding="utf-8") as file:
            results = json.load(file)
    else:
        results = []

    completed_ids = {item["audio_id"] for item in results if "error" not in item}

    print(f"\nAlready completed: {len(completed_ids)}")
    print(f"Total recordings: {len(samples)}")

    for index, sample in enumerate(samples, start=1):

        audio_id = sample["audio_id"]

        if audio_id in completed_ids:
            print(f"\nSkipping {audio_id} - already completed")
            continue

        print(f"\n[{index}/{len(samples)}] Processing {audio_id}")

        start_time = time.perf_counter()

        try:
            with open(sample["audio_path"], "rb") as audio_file:

                response = client.audio.transcriptions.create(
                    file=(Path(sample["audio_path"]).name, audio_file),
                    model=MODEL,
                    language="en",
                    temperature=0.0,
                    response_format="verbose_json",
                )

            processing_time = time.perf_counter() - start_time

            result = {
                "audio_id": audio_id,
                "speaker_id": sample["speaker_id"],
                "model": MODEL,
                "reference": sample["reference"],
                "prediction": response.text.strip(),
                "audio_duration_seconds": response.duration,
                "processing_time_seconds": round(processing_time, 3),
            }

            results = [item for item in results if item["audio_id"] != audio_id]
            results.append(result)

            save_results(results)

            print("Prediction:", result["prediction"])
            print(f"Processing time: {processing_time:.3f} seconds")

        except Exception as error:
            processing_time = time.perf_counter() - start_time

            print(f"ERROR processing {audio_id}: {error}")

            error_result = {
                "audio_id": audio_id,
                "speaker_id": sample["speaker_id"],
                "error": str(error),
                "processing_time_seconds": round(processing_time, 3),
            }

            results = [item for item in results if item["audio_id"] != audio_id]
            results.append(error_result)
            save_results(results)

            # Stop on API errors to avoid repeated quota failures.
            print("\nStopping benchmark after an API error.")
            break

    return results


# --------------------------------------------------
# 6. EVALUATE OVERALL WER AND CER
# --------------------------------------------------


def evaluate_results(results):

    successful = [
        item
        for item in results
        if "error" not in item and item.get("prediction") is not None
    ]

    if not successful:
        print("\nNo successful transcriptions to evaluate.")
        return

    references = [normalize_text(item["reference"]) for item in successful]

    predictions = [normalize_text(item["prediction"]) for item in successful]

    word_result = process_words(references, predictions)
    char_result = process_characters(references, predictions)

    total_audio = sum(item.get("audio_duration_seconds", 0) for item in successful)

    total_processing = sum(
        item.get("processing_time_seconds", 0) for item in successful
    )

    print("\n" + "=" * 55)
    print("LIBRISPEECH BENCHMARK RESULTS")
    print("=" * 55)

    print(f"Model                 : {MODEL}")
    print(f"Successful recordings : {len(successful)}")
    print(f"Failed recordings     : {len(results) - len(successful)}")
    print(
        f"Speakers              : {len(set(item['speaker_id'] for item in successful))}"
    )

    print(f"\nTotal audio duration  : {total_audio:.2f} seconds")
    print(f"Total API time        : {total_processing:.2f} seconds")

    if successful:
        print(
            f"Average API time      : "
            f"{total_processing / len(successful):.3f} seconds"
        )

    print(f"\nWER                   : {word_result.wer * 100:.2f}%")
    print(f"CER                   : {char_result.cer * 100:.2f}%")

    print(f"Word substitutions    : {word_result.substitutions}")
    print(f"Word deletions        : {word_result.deletions}")
    print(f"Word insertions       : {word_result.insertions}")

    print("=" * 55)


# --------------------------------------------------
# 7. MAIN
# --------------------------------------------------

if __name__ == "__main__":

    samples = load_samples()

    print(f"Loaded {len(samples)} recordings.")

    results = transcribe_samples(samples)

    evaluate_results(results)

    print(f"\nResults saved to: {RESULTS_FILE}")

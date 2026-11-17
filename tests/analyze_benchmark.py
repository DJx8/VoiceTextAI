import json
import re
from pathlib import Path
from jiwer import process_words

RESULTS_FILE = Path(__file__).parent / "benchmark_results.json"


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


with open(RESULTS_FILE, "r", encoding="utf-8") as file:
    results = json.load(file)


total_errors = 0
total_words = 0

print("\nINDIVIDUAL RECORDING ANALYSIS")
print("=" * 75)

for item in results:

    if "error" in item:
        continue

    reference = normalize_text(item["reference"])
    prediction = normalize_text(item["prediction"])

    evaluation = process_words(reference, prediction)

    errors = evaluation.substitutions + evaluation.deletions + evaluation.insertions

    total_errors += errors
    total_words += evaluation.hits + evaluation.substitutions + evaluation.deletions

    if errors > 0:
        print(f"\nAudio ID: {item['audio_id']}")
        print(f"Speaker : {item['speaker_id']}")
        print(f"WER     : {evaluation.wer * 100:.2f}%")
        print(f"Errors  : {errors}")
        print(f"Reference : {reference}")
        print(f"Prediction: {prediction}")

print("\n" + "=" * 75)
print("SUMMARY")
print("=" * 75)

if total_words:
    print(f"Total reference words: {total_words}")
    print(f"Total word errors   : {total_errors}")
    print(f"Overall WER         : {total_errors / total_words * 100:.2f}%")

import json
import re
from pathlib import Path
from jiwer import process_words

RESULTS_FILE = Path(__file__).parent / "benchmark_results.json"


def strict_normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalized_text(text):
    text = strict_normalize(text)

    # Standardize common British/American spelling differences.
    spelling_map = {
        "sceptical": "skeptical",
        "colour": "color",
        "favour": "favor",
        "honour": "honor",
        "labour": "labor",
    }

    words = text.split()
    words = [spelling_map.get(word, word) for word in words]

    return " ".join(words)


def calculate_wer(results, normalizer, label):
    references = []
    predictions = []

    for item in results:
        if "error" in item:
            continue

        references.append(normalizer(item["reference"]))
        predictions.append(normalizer(item["prediction"]))

    evaluation = process_words(references, predictions)

    print(f"\n{label}")
    print("-" * 45)
    print(f"WER             : {evaluation.wer * 100:.2f}%")
    print(f"Correct words   : {evaluation.hits}")
    print(f"Substitutions   : {evaluation.substitutions}")
    print(f"Deletions       : {evaluation.deletions}")
    print(f"Insertions      : {evaluation.insertions}")


with open(RESULTS_FILE, "r", encoding="utf-8") as file:
    results = json.load(file)

print("=" * 50)
print("WHISPER LARGE V3 - DUAL WER EVALUATION")
print("=" * 50)

calculate_wer(results, strict_normalize, "STRICT WER")
calculate_wer(results, normalized_text, "SPELLING-NORMALIZED WER")

print("\nEvaluation completed.")

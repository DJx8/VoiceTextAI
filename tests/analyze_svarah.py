import json
import re
from pathlib import Path
from collections import defaultdict

from jiwer import wer, cer, process_words

INPUT_FILE = Path("tests/benchmark_results_svarah.json")


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

results = [item for item in results if "reference" in item and "prediction" in item]

print(f"Successful recordings: {len(results)}")

# ---------------- INDIVIDUAL ERROR ANALYSIS ----------------

analysed = []

for item in results:
    reference = normalize_text(item["reference"])
    prediction = normalize_text(item["prediction"])

    stats = process_words(reference, prediction)

    analysed.append(
        {
            "index": item["sample_index"] + 1,
            "state": item["state"],
            "language": item["native_language"],
            "duration": item["duration_seconds"],
            "wer": stats.wer,
            "cer": cer(reference, prediction),
            "substitutions": stats.substitutions,
            "deletions": stats.deletions,
            "insertions": stats.insertions,
        }
    )

# ---------------- WORST RECORDINGS ----------------

print("\n=== 10 RECORDINGS WITH HIGHEST WER ===")

worst = sorted(analysed, key=lambda x: x["wer"], reverse=True)[:10]

for item in worst:
    print(
        f"Sample {item['index']:02d} | "
        f"Language: {item['language']:<12} | "
        f"State: {item['state']:<16} | "
        f"Duration: {item['duration']:.2f}s | "
        f"WER: {item['wer'] * 100:.2f}% | "
        f"S:{item['substitutions']} "
        f"D:{item['deletions']} "
        f"I:{item['insertions']}"
    )

# ---------------- LANGUAGE ANALYSIS ----------------

language_groups = defaultdict(lambda: {"refs": [], "preds": []})

for item in results:
    language = item["native_language"]

    language_groups[language]["refs"].append(normalize_text(item["reference"]))

    language_groups[language]["preds"].append(normalize_text(item["prediction"]))

print("\n=== PERFORMANCE BY NATIVE LANGUAGE ===")

for language, group in sorted(
    language_groups.items(), key=lambda x: x[1]["refs"].__len__(), reverse=True
):
    score = wer(group["refs"], group["preds"])
    character_score = cer(group["refs"], group["preds"])

    print(
        f"{language:<12} | "
        f"Samples: {len(group['refs']):2d} | "
        f"WER: {score * 100:6.2f}% | "
        f"CER: {character_score * 100:6.2f}%"
    )

# ---------------- STATE ANALYSIS ----------------

state_groups = defaultdict(lambda: {"refs": [], "preds": []})

for item in results:
    state = item["state"]

    state_groups[state]["refs"].append(normalize_text(item["reference"]))

    state_groups[state]["preds"].append(normalize_text(item["prediction"]))

print("\n=== PERFORMANCE BY STATE ===")

for state, group in sorted(
    state_groups.items(), key=lambda x: x[1]["refs"].__len__(), reverse=True
):
    print(
        f"{state:<18} | "
        f"Samples: {len(group['refs']):2d} | "
        f"WER: {wer(group['refs'], group['preds']) * 100:.2f}%"
    )

print("\nAnalysis complete.")

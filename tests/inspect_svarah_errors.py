import json
import re
from pathlib import Path

INPUT_FILE = Path("tests/benchmark_results_svarah.json")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

results = [item for item in results if "reference" in item and "prediction" in item]


def redact_numbers(text):
    # Avoid displaying possible phone numbers or long numeric identifiers.
    return re.sub(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)", "[REDACTED NUMBER]", text)


selected_indices = [34, 19, 43, 10, 13, 16, 46, 39, 31, 40]

print("=== DETAILED TRANSCRIPTION ERROR INSPECTION ===")

for sample_number in selected_indices:
    item = next((x for x in results if x["sample_index"] + 1 == sample_number), None)

    if item is None:
        continue

    print("\n" + "=" * 65)
    print(f"Sample: {sample_number}")
    print(f"Native language: {item['native_language']}")
    print(f"State: {item['state']}")
    print(f"Duration: {item['duration_seconds']:.2f} seconds")

    print("\nREFERENCE:")
    print(redact_numbers(item["reference"]))

    print("\nWHISPER PREDICTION:")
    print(redact_numbers(item["prediction"]))

print("\nInspection complete.")

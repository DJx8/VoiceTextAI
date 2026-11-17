import json
import re
from pathlib import Path

from jiwer import wer, cer, process_words

# -----------------------------------------
# 1. Project paths
# -----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REFERENCE_FILE = PROJECT_ROOT / "tests" / "reference_transcript.txt"
TRANSCRIPTION_FILE = PROJECT_ROOT / "tests" / "transcription_result.json"
OUTPUT_FILE = PROJECT_ROOT / "tests" / "evaluation_result.json"


# -----------------------------------------
# 2. Text normalization
# -----------------------------------------


def normalize_text(text):
    """
    Convert text to lowercase and remove punctuation.
    This avoids counting capitalization and punctuation
    differences as transcription errors.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------------------
# 3. Load reference and prediction
# -----------------------------------------

if not REFERENCE_FILE.exists():
    raise FileNotFoundError("Reference transcript not found.")

if not TRANSCRIPTION_FILE.exists():
    raise FileNotFoundError("Transcription result not found.")

reference = REFERENCE_FILE.read_text(encoding="utf-8")

with open(TRANSCRIPTION_FILE, "r", encoding="utf-8") as file:
    transcription_data = json.load(file)

prediction = transcription_data["text"]

reference_clean = normalize_text(reference)
prediction_clean = normalize_text(prediction)


# -----------------------------------------
# 4. Calculate WER and CER
# -----------------------------------------

word_error_rate = wer(reference_clean, prediction_clean)
character_error_rate = cer(reference_clean, prediction_clean)

word_details = process_words(reference_clean, prediction_clean)


# -----------------------------------------
# 5. Extract error counts
# -----------------------------------------

substitutions = word_details.substitutions
insertions = word_details.insertions
deletions = word_details.deletions

hits = word_details.hits

total_words = hits + substitutions + deletions


# -----------------------------------------
# 6. Display evaluation
# -----------------------------------------

print("=" * 55)
print("       VOICETEXT AI - ACCURACY EVALUATION")
print("=" * 55)

print("\nREFERENCE TRANSCRIPT:")
print(reference)

print("\nPREDICTED TRANSCRIPT:")
print(prediction)

print("\n" + "-" * 55)
print("WORD ERROR RATE (WER)")
print("-" * 55)

print(f"Total reference words : {total_words}")
print(f"Correct words         : {hits}")
print(f"Substitutions         : {substitutions}")
print(f"Insertions            : {insertions}")
print(f"Deletions             : {deletions}")
print(f"WER                   : {word_error_rate:.4f}")
print(f"WER percentage        : {word_error_rate * 100:.2f}%")

print("\n" + "-" * 55)
print("CHARACTER ERROR RATE (CER)")
print("-" * 55)

print(f"CER                   : {character_error_rate:.4f}")
print(f"CER percentage        : {character_error_rate * 100:.2f}%")

print("\n" + "-" * 55)

# -----------------------------------------
# 7. Save evaluation results
# -----------------------------------------

results = {
    "model": transcription_data["model"],
    "wer": round(word_error_rate, 4),
    "wer_percentage": round(word_error_rate * 100, 2),
    "cer": round(character_error_rate, 4),
    "cer_percentage": round(character_error_rate * 100, 2),
    "total_reference_words": total_words,
    "correct_words": hits,
    "substitutions": substitutions,
    "insertions": insertions,
    "deletions": deletions,
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4, ensure_ascii=False)

print(f"Evaluation saved to: {OUTPUT_FILE}")
print("\nEvaluation completed successfully!")

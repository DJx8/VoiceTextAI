from datasets import load_dataset, Audio
from collections import Counter

SAMPLE_LIMIT = 50

print("Loading Svarah in streaming mode...")

dataset = load_dataset("ai4bharat/Svarah", split="test", streaming=True, token=True)

dataset = dataset.cast_column("audio_filepath", Audio(decode=False))

print(f"\nInspecting first {SAMPLE_LIMIT} samples...")

samples = []

for sample in dataset:
    samples.append(sample)

    if len(samples) >= SAMPLE_LIMIT:
        break

print(f"\nSuccessfully retrieved: {len(samples)} samples")

print("\n=== LANGUAGE BACKGROUND ===")
for language, count in Counter(s["primary_language"] for s in samples).most_common():
    print(f"{language}: {count}")

print("\n=== STATE DISTRIBUTION ===")
for state, count in Counter(s["native_place_state"] for s in samples).most_common():
    print(f"{state}: {count}")

print("\n=== GENDER DISTRIBUTION ===")
for gender, count in Counter(s["gender"] for s in samples).most_common():
    print(f"{gender}: {count}")

print("\n=== AGE DISTRIBUTION ===")
for age, count in Counter(s["age-group"] for s in samples).most_common():
    print(f"{age}: {count}")

print("\n=== AUDIO STATISTICS ===")

durations = [s["duration"] for s in samples]

print(f"Total duration: {sum(durations):.2f} seconds")
print(f"Average duration: {sum(durations)/len(durations):.2f} seconds")
print(f"Shortest: {min(durations):.2f} seconds")
print(f"Longest: {max(durations):.2f} seconds")

print("\n=== FIRST 5 TRANSCRIPTS ===")

for i, sample in enumerate(samples[:5], start=1):
    print(f"\n{i}.")
    print("State:", sample["native_place_state"])
    print("Native language:", sample["primary_language"])
    print("Transcript:", sample["text"])

print("\n=== INSPECTION COMPLETE ===")

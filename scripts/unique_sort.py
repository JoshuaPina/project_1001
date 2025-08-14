#Importing Libraries

import pandas as pd
from tqdm import tqdm

# Function to track steps taken
def print_step(step_number: int, message: str) -> None:
    tqdm.write(f"[Step {step_number}] {message}")


df = pd.read_csv('data/unique_words.csv')
print("-"*60)
print_step(1, "Libraries and DataFrame Loaded Successfully.")
print()

df["Word"] = df["Word"].str.lower()
print_step(2, "Lowercased all words.")
print()

df = df.sort_values(by="Word", ascending=True)
print_step(3, "Sorted all words alphabetically.")
print()

df = df.reset_index(drop=True)
print_step(4, "Reset index.")
print()

df.to_csv("unique_words_sorted.csv", index=False, header=False)
print_step(5, "Saved sorted words to unique_words_sorted.csv.")
print()

print(f"The new sorted list contains {len(df)} words.")
print("-"*60)
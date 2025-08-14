from pathlib import Path
import pandas as pd
from tqdm import tqdm
import random

# Function to label steps quickly.
def print_step(step_number, message):
    print("-" * 70)
    tqdm.write("")  
    tqdm.write(f"[Step {step_number}] {message}")
    tqdm.write("")  
# Creating easier paths
BASE_DIR = Path.home() / "OneDrive - Georgia State University" / "Dojo" / "Projects" / "Work" / "Ruminations" / "project1001"
file_path = BASE_DIR / "data" / "unique_words_sorted.csv"

# Actual start of script is here

df = pd.read_csv(file_path, header=None)
df.columns = ["word"]

print_step(1, "Libraries, path, and dataframe loaded with column header.")
print_step(2, "Displaying the first 5 rows of the dataframe to confirm.")
print(df.head())

print_step(3, "Creating a dictionary from the dataframe.")
word_dict = {i+1: word for i, word in enumerate(df["word"])}
print("First 10 dict items for validation:")
print()
for word, number in list(word_dict.items())[:10]:
    print(f"{word}: {number}")

print_step(4, "Starting random word selection generator.")
random_word = random.choice(list(word_dict.keys()))
print(f"Randomly selected word: {word_dict[random_word]} (Number: {random_word})")
print()
# Error in code here, this actually just confirms if the number is in the dict
selected_word = (int(input("Select a number, 1 - 981: ")))
selected_word = int(selected_word) in word_dict.keys()
print(selected_word)

user_selected_number = int(input("Select a number, 1 - 981: "))
if user_selected_number in word_dict.keys():
    print(f"You selected: {word_dict[user_selected_number]} (Number: {user_selected_number})")
else:
    print("Invalid selection.")
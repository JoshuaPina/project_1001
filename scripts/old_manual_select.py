# scripts/manual_select.py
from pathlib import Path
import pandas as pd
from datetime import datetime

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" # Folder for all data files in project1001
SUBJECTS_DIR = DATA_DIR / "public_csv" # Folder for anonymized subject files
SUBJECTS_CSV = SUBJECTS_DIR / "subjects.csv" # This allows us to use subjects.csv or subjects.xlsx
SUBJECTS_XLSX = SUBJECTS_DIR / "subjects.xlsx"

WORD_BANK_PATH = DATA_DIR / "unique_words_sorted.csv"  # 981 words, one word per line, no header
LOG_PATH = DATA_DIR / "assignments_log.csv"            # A log will be created automatically

# ---------- Loaders ----------
print("-"*50)
print("Loading subjects now!")
print("-"*50)

def load_subjects():
    # Auto-pick CSV or XLSX
    if SUBJECTS_CSV.exists():
        df = pd.read_csv(SUBJECTS_CSV, dtype=str).fillna("")
        source = SUBJECTS_CSV
    elif SUBJECTS_XLSX.exists():
        df = pd.read_excel(SUBJECTS_XLSX, dtype=str).fillna("")
        source = SUBJECTS_XLSX
    else:
        print(f"[error] No subjects file found. Create either:\n  - {SUBJECTS_CSV}\n  - {SUBJECTS_XLSX}")
        raise SystemExit(1)

    # Expect your current headers: Pseudonym, ID
    expected = {"Pseudonym", "ID"}
    if not expected.issubset(df.columns):
        print(f"[error] Subjects file at {source} must contain columns: Pseudonym, ID")
        print(f"[hint] Found columns: {list(df.columns)}")
        raise SystemExit(1)

    # Normalize to internal names
    out = pd.DataFrame({
        "subject_id": df["ID"].astype(str).str.strip(),
        "subject_name": df["Pseudonym"].astype(str).str.strip()
    })
    # Drop fully blank rows if any
    out = out[(out["subject_id"] != "") | (out["subject_name"] != "")]
    if out.empty:
        print(f"[error] No usable rows in {source}.")
        raise SystemExit(1)

    return out

print("Loading available words now!")
print("-"*50)

def load_word_bank():
    if not WORD_BANK_PATH.exists():
        print(f"[error] Missing word bank: {WORD_BANK_PATH}")
        raise SystemExit(1)
    df = pd.read_csv(WORD_BANK_PATH, header=None, names=["word"])
    df["word"] = df["word"].astype(str).str.strip()
    df["word_number"] = df.index + 1
    return df[["word_number", "word"]]

def load_log():
    if not LOG_PATH.exists():
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=[
            "timestamp","subject_id","subject_name",
            "assignment_number","word_number","word"
        ]).to_csv(LOG_PATH, index=False)
    return pd.read_csv(LOG_PATH)

# ---------- Helpers ----------
def next_assignment_number(subject_id: str) -> int:
    log = load_log()
    rows = log[log["subject_id"] == subject_id]
    return 1 if rows.empty else int(rows["assignment_number"].max()) + 1

def word_used(subject_id: str, word_number: int) -> bool:
    log = load_log()
    if log.empty:
        return False
    m = (log["subject_id"] == subject_id) & (log["word_number"] == word_number)
    return bool(m.any())

def append_log(subject_id, subject_name, assignment_number, word_number, word):
    log = load_log()
    new = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "subject_id": subject_id,
        "subject_name": subject_name,
        "assignment_number": int(assignment_number),
        "word_number": int(word_number),
        "word": word
    }
    log = pd.concat([log, pd.DataFrame([new])], ignore_index=True)
    log.to_csv(LOG_PATH, index=False)

# ---------- Interactive UI ----------
print("Loading CLI now!")
print("-"*50)

def choose_subject(df: pd.DataFrame):
    print("\nWho should learn a new word today?")
    for i, r in enumerate(df.itertuples(index=False), start=1):
        # Example: " 1. S-001 — Wife Platypus"
        print(f" {i}. {r.subject_id} — {r.subject_name}")
    while True:
        raw = input("Enter row number or subject_id: ").strip()
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(df):
                row = df.iloc[idx-1]
                return row["subject_id"], row["subject_name"]
            print("Out of range. Try again.")
        else:
            match = df[df["subject_id"].str.casefold() == raw.casefold()]
            if not match.empty:
                r = match.iloc[0]
                return r["subject_id"], r["subject_name"]
            print("Not found. Try again.")

def choose_word_number(max_n: int):
    while True:
        raw = input(f"Enter word number (1 to {max_n}): ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= max_n:
                return n
        print("Invalid number. Try again.")


def main():
    subjects = load_subjects()
    bank = load_word_bank()

    subject_id, subject_name = choose_subject(subjects)

    while True:
        number = choose_word_number(len(bank))
        if word_used(subject_id, number):
            print(f"[blocked] Word #{number} already used for {subject_id}. Pick another.")
            continue
        word = bank.iloc[number-1].word
        assign_no = next_assignment_number(subject_id)
        append_log(subject_id, subject_name, assign_no, number, word)
        print(f"\nSaved {subject_id} ({subject_name}) — assignment #{assign_no}")
        print(f"         {word}  (Number: {number})")
        break

if __name__ == "__main__":
    main()

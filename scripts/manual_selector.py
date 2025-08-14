# scripts/manual_select.py
from pathlib import Path
import pandas as pd
from datetime import datetime
import random

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR      = PROJECT_ROOT / "data"
SUBJECTS_DIR  = DATA_DIR / "public_csv"
SUBJECTS_CSV  = SUBJECTS_DIR / "subjects.csv"
SUBJECTS_XLSX = SUBJECTS_DIR / "subjects.xlsx"
WORD_BANK_PATH = DATA_DIR / "unique_words_sorted.csv"   # 981 words, 1 per line
LOG_PATH       = DATA_DIR / "assignments_log.csv"       # created automatically
MAP_PATH       = DATA_DIR / "word_map.csv"              # number -> word_number permutation

# ---------- Loaders ----------
print("-"*50)
print("Loading subjects now!")
print("-"*50)

def load_subjects():
    if SUBJECTS_CSV.exists():
        df = pd.read_csv(SUBJECTS_CSV, dtype=str).fillna("")
        source = SUBJECTS_CSV
    elif SUBJECTS_XLSX.exists():
        df = pd.read_excel(SUBJECTS_XLSX, dtype=str).fillna("")
        source = SUBJECTS_XLSX
    else:
        print(f"[error] No subjects file found. Create either:\n  - {SUBJECTS_CSV}\n  - {SUBJECTS_XLSX}")
        raise SystemExit(1)

    need = {"Pseudonym", "ID"}
    if not need.issubset(df.columns):
        print(f"[error] Subjects file at {source} must contain columns: Pseudonym, ID")
        print(f"[hint] Found columns: {list(df.columns)}")
        raise SystemExit(1)

    out = pd.DataFrame({
        "subject_id":   df["ID"].astype(str).str.strip(),
        "subject_name": df["Pseudonym"].astype(str).str.strip()
    })
    out = out[(out["subject_id"] != "") | (out["subject_name"] != "")]
    if out.empty:
        print(f"[error] No usable rows in {source}.")
        raise SystemExit(1)
    return out

print("Loading words now!")
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

# ---------- Mapping (randomized number -> word_number) ----------
print("Mapping words randomly now!")
print("-"*50)

def get_or_create_mapping(n_words: int) -> pd.DataFrame:
    """
    Ensures a persistent permutation so user input 'k' maps to a randomized word_number.
    Creates data/word_map.csv if it doesn't exist. Columns: number, word_number
    """
    if MAP_PATH.exists():
        m = pd.read_csv(MAP_PATH)
        # if size changed (unlikely), regenerate
        if len(m) == n_words and {"number","word_number"}.issubset(m.columns):
            return m[["number","word_number"]]
        else:
            print("[warn] Regenerating mapping (size/columns mismatch).")
    # create new permutation
    perm = list(range(1, n_words + 1))
    random.shuffle(perm)
    m = pd.DataFrame({"number": range(1, n_words + 1), "word_number": perm})
    m.to_csv(MAP_PATH, index=False)
    return m

# ---------- Helpers ----------
def next_assignment_number(subject_id: str) -> int:
    log = load_log()
    rows = log[log["subject_id"] == subject_id]
    return 1 if rows.empty else int(rows["assignment_number"].max()) + 1

def word_used(subject_id: str, word_number: int) -> bool:
    log = load_log()
    if log.empty:
        return False
    mask = (log["subject_id"] == subject_id) & (log["word_number"] == word_number)
    return bool(mask.any())

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
    print("\nSelect a subject:")
    for i, r in enumerate(df.itertuples(index=False), start=1):
        print(f" {i}. {r.subject_id} — {r.subject_name}")
    while True:
        raw = input("\nEnter row number or subject_id: ").strip()
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

def choose_number(max_n: int) -> int:
    while True:
        raw = input(f"Enter a number (1 to {max_n}): ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= max_n:
                return n
        print("Invalid number. Try again.")

def action_menu() -> str:
    print("\nWhat's next?")
    print("  [N] Pick another number for SAME subject")
    print("  [S] Switch subject")
    print("  [Q] Quit")
    while True:
        c = input("Choose N/S/Q: ").strip().lower()
        if c in {"n","s","q"}:
            return c
        print("Please enter N, S, or Q.")

# ---------- Main ----------
def main():
    subjects = load_subjects()
    bank = load_word_bank()
    mapping = get_or_create_mapping(len(bank))  # persistent permutation

    subject_id, subject_name = choose_subject(subjects)

    while True:
        # user enters any number; map it to a randomized word_number
        k = choose_number(len(bank))  # 1..N
        mapped_word_number = int(mapping.iloc[k-1]["word_number"])

        # enforce per-subject no-reuse
        if word_used(subject_id, mapped_word_number):
            print(f"[blocked] That number maps to a word already used for {subject_id}. Pick another.")
            continue

        # get the actual word
        word_row = bank.iloc[mapped_word_number - 1]
        assign_no = next_assignment_number(subject_id)
        append_log(subject_id, subject_name, assign_no, int(word_row.word_number), word_row.word)

        print(f"\nSaved ✓  {subject_id} ({subject_name}) — assignment #{assign_no}")
        print(f"         {word_row.word}  (Mapped from number: {k} → word #{mapped_word_number})")

        # next action
        choice = action_menu()
        if choice == "n":
            # stay on same subject; continue loop
            continue
        elif choice == "s":
            subject_id, subject_name = choose_subject(subjects)
            continue
        else:  # 'q'
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()

from pathlib import Path
import pandas as pd

BASE_DIR = Path.home() / "OneDrive - Georgia State University" / "Dojo" / "Projects" / "Work" / "Ruminations" / "project1001"
WORD_BANK_PATH = BASE_DIR / "data" / "unique_words_sorted.csv"
LOG_PATH = BASE_DIR / "data" / "assignments_log.csv"  # long-form log

def load_word_bank():
    df = pd.read_csv(WORD_BANK_PATH, header=None, names=["word"])
    df["word"] = df["word"].astype(str).str.strip()
    df["word_number"] = df.index + 1
    return df[["word_number", "word"]]

def ensure_log_exists():
    if not LOG_PATH.exists():
        pd.DataFrame(columns=["subject_id","subject_name","assignment_number","word_number","word"]).to_csv(LOG_PATH, index=False)

def load_log():
    ensure_log_exists()
    return pd.read_csv(LOG_PATH)

def has_subject_word(subject_id: str, word_number: int) -> bool:
    log = load_log()
    if log.empty:
        return False
    m = (log["subject_id"] == subject_id) & (log["word_number"] == word_number)
    return bool(m.any())

def next_assignment_number_for(subject_id: str) -> int:
    log = load_log()
    if log.empty:
        return 1
    rows = log[log["subject_id"] == subject_id]
    return 1 if rows.empty else int(rows["assignment_number"].max()) + 1

def append_assignment(subject_id: str, subject_name: str, assignment_number: int, word_number: int, word: str):
    log = load_log()
    new_row = {"subject_id": subject_id, "subject_name": subject_name,
               "assignment_number": assignment_number, "word_number": word_number, "word": word}
    log = pd.concat([log, pd.DataFrame([new_row])], ignore_index=True)
    log.to_csv(LOG_PATH, index=False)

print("Python script started")

from pathlib import Path
import hmac, hashlib, json, urllib.request, re, random
import pandas as pd
from tqdm import tqdm

# ---------- Config ----------
ENV = Path(".env")
INPUT = Path("data/subjects.xlsx")
OUTPUT = Path("data/public_csv/subjects.csv")
WL_DIR = Path("data/wordlists")
ADJ_PATH = WL_DIR / "adjectives.txt"
ANIM_PATH = WL_DIR / "animals.txt"
ADJ_COUNT = 500
ANIM_COUNT = 500

# Function to label steps quickly.
def print_step(step_number, message):
    print("-" * 50)
    tqdm.write("")
    tqdm.write(f"[Step {step_number}] {message}")
    tqdm.write("")

# ---------- Secret ----------
print_step(0, "Loading secret key from .env file")

def load_secret() -> bytes:
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("PSEUDONYM_SECRET="):
                return line.split("=", 1)[1].strip().encode()
    raise SystemExit("Add PSEUDONYM_SECRET=your-secret to .env")

# ---------- Wordlists (auto-fetch once, then reuse) ----------
print_step(1, "Ensuring wordlists are available")

def fetch_url(url: str) -> str:
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8", errors="ignore")

def ensure_wordlists():
    WL_DIR.mkdir(parents=True, exist_ok=True)
    if not ADJ_PATH.exists():
        txt = fetch_url("https://www.mit.edu/~ecprice/wordlist.10000")
        words = re.findall(r"[a-zA-Z]+", txt)
        random.shuffle(words)  # <-- shuffle to avoid alphabetical bias
        seen, adj = set(), []
        for w in words:
            c = w.capitalize()
            if c not in seen:
                seen.add(c)
                adj.append(c)
            if len(adj) >= ADJ_COUNT:
                break
        ADJ_PATH.write_text("\n".join(adj), encoding="utf-8")

    if not ANIM_PATH.exists():
        raw = fetch_url("https://raw.githubusercontent.com/dariusk/corpora/master/data/animals/common.json")
        animals = json.loads(raw).get("animals", [])
        animals = [a.strip().title() for a in animals if a.strip()]
        ANIM_PATH.write_text("\n".join(animals[:ANIM_COUNT]), encoding="utf-8")

def load_lists():
    ensure_wordlists()
    ADJ = [l.strip() for l in ADJ_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    ANIM = [l.strip() for l in ANIM_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    return ADJ, ANIM

# ---------- HMAC index generator ----------
print_step(2, "Defining HMAC-based index generator")

def start_indices(name: str, key: bytes, A: int, B: int) -> tuple[int, int]:
    norm = " ".join(name.lower().split())
    d = hmac.new(key, norm.encode(), hashlib.sha256).digest()
    return d[0] % A, d[1] % B

# ---------- Assign aliases with open addressing ----------
print_step(3, "Defining alias assignment function")

def assign_aliases(names: list[str], key: bytes, ADJ: list[str], ANIM: list[str]) -> dict[str, str]:
    A, B = len(ADJ), len(ANIM)
    used = set()
    mapping = {}
    for nm in sorted(set(names)):
        ai, bi = start_indices(nm, key, A, B)
        start_ai, start_bi = ai, bi
        while True:
            alias = f"{ADJ[ai]} {ANIM[bi]}"
            if alias not in used or mapping.get(nm) == alias:
                mapping[nm] = alias
                used.add(alias)
                break
            print(f"[collision] '{nm}' -> '{alias}' exists. Trying next combo...")
            bi = (bi + 1) % B
            if bi == start_bi:
                ai = (ai + 1) % A
                if ai == start_ai:
                    raise RuntimeError("Ran out of unique pseudonyms.")
    return mapping

# ---------- Main ----------
print_step(4, "Loading input data and processing names")

if __name__ == "__main__":
    key = load_secret()
    ADJ, ANIM = load_lists()

    df = pd.read_excel(INPUT)
    if "Name" not in df.columns:
        raise SystemExit("Expected a 'Name' column.")

    names = df["Name"].astype(str).str.strip().tolist()
    name_to_alias = assign_aliases(names, key, ADJ, ANIM)

    out = df.copy()
    out["Pseudonym"] = [name_to_alias[n] for n in names]
    out.drop(columns=["Name"], inplace=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)
    print(f"Anonymized CSV written to: {OUTPUT}")
    print("-" * 50)
print("Python script completed successfully.")
print()
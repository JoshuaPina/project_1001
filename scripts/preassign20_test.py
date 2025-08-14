# python preassign20.py S001 "Alice" 20
import sys, random
from helpers import load_word_bank, has_subject_word, next_assignment_number_for, append_assignment

def main(subject_id: str, subject_name: str, k: int = 20):
    bank = load_word_bank()
    # Available choices for this subject
    available = [r for r in bank.itertuples(index=False) if not has_subject_word(subject_id, int(r.word_number))]
    if len(available) < k:
        print(f"Only {len(available)} unused words left for {subject_id}.")
        k = len(available)

    chosen = random.sample(available, k)
    assign_no = next_assignment_number_for(subject_id)

    for i, row in enumerate(chosen, start=assign_no):
        append_assignment(subject_id, subject_name, i, int(row.word_number), row.word)

    print(f"Pre-assigned {k} words to {subject_id} ({subject_name}).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python preassign20.py <subject_id> <subject_name> [k=20]")
        sys.exit(1)
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    main(sys.argv[1], " ".join(sys.argv[2:-1] if len(sys.argv)>3 else sys.argv[2:]), k)

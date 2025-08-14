# python random_assign.py S001 "Alice"
import sys, random
from helpers import load_word_bank, has_subject_word, next_assignment_number_for, append_assignment

def main(subject_id: str, subject_name: str):
    bank = load_word_bank()

    # Build candidate set = words not yet used by this subject
    unused = []
    for row in bank.itertuples(index=False):
        if not has_subject_word(subject_id, int(row.word_number)):
            unused.append(row)

    if not unused:
        print(f"No unused words remain for {subject_id} ({subject_name}).")
        return

    chosen = random.choice(unused)
    assign_no = next_assignment_number_for(subject_id)
    append_assignment(subject_id, subject_name, assign_no, int(chosen.word_number), chosen.word)
    print(f"Assigned #{assign_no} to {subject_id} ({subject_name}): {chosen.word} (Number: {chosen.word_number})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python random_assign.py <subject_id> <subject_name>")
        sys.exit(1)
    main(sys.argv[1], " ".join(sys.argv[2:]))

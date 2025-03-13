import csv
import sys
import os
from collections import Counter


def majority_vote(items):
    counts = Counter(items)
    if not counts:
        return None
    max_count = max(counts.values())
    candidates = [item for item, count in counts.items() if count == max_count]
    for item in items:
        if item in candidates:
            return item
    return candidates[0]


def ensemble_whole(outputs):
    return majority_vote(outputs)


def ensemble_token_level(outputs):
    token_lists = [output.split() for output in outputs]
    max_tokens = max(len(tokens) for tokens in token_lists)
    result_tokens = []
    for i in range(max_tokens):
        tokens = [tokens[i] if i < len(tokens) else "" for tokens in token_lists]
        token = majority_vote(tokens)
        if token == "":
            break
        result_tokens.append(token)
    return " ".join(result_tokens)


def ensemble_char_level(outputs):
    max_length = max(len(output) for output in outputs)
    result_chars = []
    for i in range(max_length):
        chars = [output[i] if i < len(output) else "" for output in outputs]
        char = majority_vote(chars)
        if char == "":
            break
        result_chars.append(char)
    return "".join(result_chars)


def main():
    # Usage: python ensemble.py input.tsv
    input_file = sys.argv[1]
    groups = {}

    with open(input_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            key = row["ID"]
            groups.setdefault(key, []).append(row)

    prefix = os.path.splitext(os.path.basename(input_file))[0]
    whole_file = f"{prefix}_ensemble_whole.tsv"
    token_file = f"{prefix}_ensemble_token.tsv"
    char_file = f"{prefix}_ensemble_char.tsv"

    fieldnames = ["ID", "Source", "Change", "Output"]
    with open(whole_file, "w", newline="", encoding="utf-8") as wf, \
            open(token_file, "w", newline="", encoding="utf-8") as tf, \
            open(char_file, "w", newline="", encoding="utf-8") as cf:
        whole_writer = csv.DictWriter(wf, fieldnames=fieldnames, delimiter="\t")
        token_writer = csv.DictWriter(tf, fieldnames=fieldnames, delimiter="\t")
        char_writer = csv.DictWriter(cf, fieldnames=fieldnames, delimiter="\t")

        whole_writer.writeheader()
        token_writer.writeheader()
        char_writer.writeheader()

        for key, rows in groups.items():
            source = rows[0]["Source"]
            change = rows[0]["Change"]
            outputs = [row["Output"] for row in rows]

            whole_output = ensemble_whole(outputs)
            token_output = ensemble_token_level(outputs)
            char_output = ensemble_char_level(outputs)

            whole_writer.writerow({
                "ID": key,
                "Source": source,
                "Change": change,
                "Output": whole_output
            })
            token_writer.writerow({
                "ID": key,
                "Source": source,
                "Change": change,
                "Output": token_output
            })
            char_writer.writerow({
                "ID": key,
                "Source": source,
                "Change": change,
                "Output": char_output
            })


if __name__ == "__main__":
    main()

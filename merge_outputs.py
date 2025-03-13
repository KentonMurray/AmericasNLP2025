import sys
import csv
from collections import defaultdict


def read_tsv(filename):
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def write_tsv(filename, rows, fieldnames):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def get_output(row, header):
    # assuming hypothesis is in the last column
    pred_field = header[-1]
    return row[pred_field]


def merge_files(orig_tag, orig_file, sys_files):
    """
    Merge all files, sorting so that the reference file comes first for each example
    """
    merged = []

    # first add all reference rows
    orig_rows = read_tsv(orig_file)
    for row in orig_rows:
        new_row = {
            "ID": row["ID"],
            "Source": row["Source"],
            "Change": row["Change"],
            "System": orig_tag,
            "Output": row["Target"]
        }
        merged.append(new_row)

    # add all output rows
    for sys_tag, sys_file in sys_files:
        with open(sys_file, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            header = reader.fieldnames
            for row in reader:
                new_row = {
                    "ID": row["ID"],
                    "Source": row["Source"],
                    "Change": row["Change"],
                    "System": sys_tag,
                    "Output": get_output(row, header)
                }
                merged.append(new_row)

    # reference row comes first for each example
    merged.sort(key=lambda r: (r["ID"], 0 if r["System"] == orig_tag else 1))
    return merged


def process_simple(merged_rows, orig_tag):
    """
    1. Wraps the source sentence in [square brackets]
    2. Marks output tokens that are not present in the reference with "#"
    3. Marks output sentences that are not an exact match to the reference with "* "
    """

    groups = defaultdict(list)
    for row in merged_rows:
        groups[row["ID"]].append(row)

    processed_rows = []
    for ID, group in groups.items():
        # get the reference row for this example
        ref_row = next((row for row in group if row["System"] == orig_tag), None)
        if not ref_row:
            continue
        ref_sentence = ref_row["Output"].strip()
        ref_tokens = set(ref_sentence.split())
        for r in group:
            # wrap source sentence in square brackets.
            r["Source"] = f"[{r['Source']}]"
            predicted = r["Output"].strip()
            tokens = predicted.split()

            # mark tokens that are not found in the reference
            # ignores ordering of tokens
            modified_tokens = []
            for token in tokens:
                if token not in ref_tokens:
                    modified_tokens.append("#" + token)
                else:
                    modified_tokens.append(token)
            modified_sentence = " ".join(modified_tokens)

            # mark a sentence for not being an exact match
            # sentences where all tokens are present but in the correct order are marked here
            if predicted != ref_sentence:
                modified_sentence = "* " + modified_sentence
            r["Output"] = modified_sentence
            processed_rows.append(r)

    return processed_rows


def main():
    # Usage: python merge_outputs.py LANG ORIG_TAG original.tsv [SYS_TAG sys_file.tsv] ...
    lang = sys.argv[1]
    orig_tag = sys.argv[2]
    orig_file = sys.argv[3]
    sys_files = []
    i = 4

    # each output file
    while i < len(sys.argv):
        sys_files.append((sys.argv[i], sys.argv[i + 1]))
        i += 2

    # just merge all the outputs first and save that
    merged = merge_files(orig_tag, orig_file, sys_files)
    merged_fieldnames = ["ID", "Source", "Change", "System", "Output"]
    merged_out = f"{lang}-merged.tsv"
    write_tsv(merged_out, merged, merged_fieldnames)
    print(f"Merged file saved as '{merged_out}'.")

    # then for each output sentence, prepend "*" for incorrect sentences
    # and "#" for tokens that do not appear in the reference
    processed = process_simple(merged, orig_tag)
    processed_out = f"{lang}-processed.tsv"
    write_tsv(processed_out, processed, merged_fieldnames)
    print(f"Processed file saved as '{processed_out}'.")


if __name__ == "__main__":
    main()

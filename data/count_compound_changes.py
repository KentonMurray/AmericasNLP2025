import csv
import sys
import glob


def count_comma_changes(filename):
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        total_rows = 0
        compound_change_rows = 0
        total_compound_changes = 0

        for row in reader:
            total_rows += 1
            num_compound_changes = row['Change'].count(',')
            total_compound_changes += num_compound_changes
            if num_compound_changes > 0:
                compound_change_rows += 1

        avg = (total_compound_changes / total_rows + 1) if total_rows > 0 else 1
        print(f"{filename}:  {compound_change_rows}/{total_rows}, Avg = {avg:.2f} per row")


if __name__ == "__main__":
    tsv_files = glob.glob("*.tsv")

    for tsv_file in tsv_files:
        count_comma_changes(tsv_file)
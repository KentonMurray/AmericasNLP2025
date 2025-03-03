import csv
import glob


def count_comma_changes(filename):
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        total_rows = 0
        comma_rows = 0

        for row in reader:
            total_rows += 1
            if ',' in row['Change']:
                comma_rows += 1

        fraction = comma_rows / total_rows if total_rows > 0 else 0
        print(f"{filename}: {comma_rows}/{total_rows}")


if __name__ == "__main__":
    tsv_files = glob.glob("*.tsv")  # Adjust this pattern if needed

    for tsv_file in tsv_files:
        count_comma_changes(tsv_file)
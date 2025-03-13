import pandas as pd
import subprocess
import argparse
import os


def tag_sentence(sentence, language):
    try:
        result = subprocess.run(
            ["apertium", "-d", f"apertium-{language}", "-n", f"{language}-tagger"],
            input=sentence, text=True, capture_output=True
        )
        # print(result.stdout.strip())
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("language")

    args = parser.parse_args()

    input_file = args.input_file
    language = args.language

    base_name, _ = os.path.splitext(input_file)
    output_file = f"{base_name}-tagged.tsv"

    df = pd.read_csv(input_file, sep="\t")

    df["Source-Tagged"] = df["Source"].apply(lambda sentence: tag_sentence(sentence, language))
    df.to_csv(output_file, sep="\t", index=False)

    print(f"Results saved in {output_file}")
    print(df.head())



if __name__ == "__main__":
    main()

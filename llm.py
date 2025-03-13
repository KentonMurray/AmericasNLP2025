import argparse
import sys
import os
from openai import OpenAI
from sacrebleu.metrics import BLEU, CHRF
from dotenv import load_dotenv
import re
from tqdm import tqdm
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# FutureWarning from pandas for this line: final_selection = pd.concat([selected_exact, partials_df], ignore_index=True)
# when either selected_exact or partials_df is empty
import pandas as pd

# background info kept in separate file to avoid making public copyrighted textbook material
from create_language_dict import background_info

load_dotenv()


bleu = BLEU()
chrf = CHRF()

language_dict = {
    'bribri':'Bribri',
    'guarani':'Guaraní',
    'maya':'Yucatec Maya',
    'nahuatl_omitlan':'Western Sierra Puebla Nahuatl'
}

def combined_bleu_chrf_score(hypothesis: str, reference: str) -> float:
    chrf_score = chrf.corpus_score([hypothesis], [[reference]]).score
    bleu_score = bleu.corpus_score([hypothesis], [[reference]]).score
    # negative score to put higher score first when sorting by ascending order
    return -(bleu_score + chrf_score)


def select_examples(
        train_df: pd.DataFrame,
        test_row: pd.Series,
        max_examples: int = 5
) -> pd.DataFrame:
    """ Returns a dataframe of training examples to include in the prompt

    Select up to max_examples from train_df that match test_row's tags, sorted by combined BLEU+chrF
    If necessary, more examples are selected based on partial overlap of tags
    """

    test_tags = set(t.strip() for t in test_row["Change"].split(","))

    # handle exact matches
    exact_matches = train_df[train_df["TagSet"].apply(lambda s: s == test_tags)].copy()

    exact_matches["SortScore"] = exact_matches["Source"].apply(
        lambda hyp: combined_bleu_chrf_score(hyp, test_row["Source"])
    )
    exact_matches.sort_values(by="SortScore", inplace=True)
    selected_exact = exact_matches.head(max_examples) # up to max_examples matches

    if len(selected_exact) >= max_examples:
        return selected_exact

    # if more examples are needed, search for partial overlaps
    needed = max_examples - len(selected_exact)
    partials_list = []
    num_test_tags = len(test_tags)

    for overlap_size in range(num_test_tags - 1, 0, -1):
        # each row will fall into a single overlap_size bucket
        subset = train_df[
            train_df["TagSet"].apply(lambda s: len(s.intersection(test_tags)) == overlap_size)
        ].copy()

        if subset.empty:
            continue

        subset["SortScore"] = subset["Source"].apply(
            lambda hyp: combined_bleu_chrf_score(hyp, test_row["Source"])
        )
        subset.sort_values(by="SortScore", inplace=True)
        partials_list.append(subset)

        if sum(len(x) for x in partials_list) >= needed:
            break

    partials_df = None
    if partials_list:
        partials_df = pd.concat(partials_list).head(needed)

    final_selection = pd.concat([selected_exact, partials_df], ignore_index=True)

    return final_selection


def build_prompt(
    language: str,
    examples: pd.DataFrame,
    test_example: dict,
    use_pos=False,
    use_background=False,
    use_descriptive=False,
    use_chain_of_thought=False
) -> str:
    user_prompt = (
        f"This is a linguistic puzzle involving grammar changes in {language_dict[language]}."
        " You are given examples which include a source sentence"
    )

    if use_pos and test_example.get("Source-Tagged"):
        user_prompt += ", part of speech tags"
    user_prompt += (
        ", a grammar change to apply to the source sentence, and a target sentence."
    )
    if use_background:
        user_prompt += " You are also given additional information about the morphology and syntax of the language."
    user_prompt += " Your task is to generate the target sentence for the final example.\n"

    if use_background:
        user_prompt += f"\nHere is some additional information about {language_dict[language]}:\n {background_info[language]}\n"

    # included training examples
    num_ex = 0
    for _, ex in examples.iterrows():
        num_ex += 1
        user_prompt += f"\nExample {num_ex}:\n"
        user_prompt += f"Source: {ex['Source']}\n"
        if use_pos and "Source-Tagged" in ex and ex["Source-Tagged"]:
            user_prompt += f"Part of Speech Tags: {ex['Source-Tagged']}]\n"
        if use_descriptive:
            grammar_change_line = f"Grammar Change: {ex['Change']}" # TODO more descriptive tag
        else:
            grammar_change_line = f"Grammar Change: {ex['Change']}"
        user_prompt += grammar_change_line + "\n"
        user_prompt += f"Target: {ex['Target']}\n"

    # test sentence
    user_prompt += (
        "\nNow generate the target sentence for this example:\n"
        f"Source: {test_example['Source']}\n"
    )

    if use_pos and test_example.get("Source-Tagged"):
        user_prompt += f"Part of Speech Tags: {test_example['Source-Tagged']}\n"
    if use_descriptive:
        grammar_change_line = f"Grammar Change: {test_example['Change']}"  # TODO more descriptive tag
    else:
        grammar_change_line = f"Grammar Change: {test_example['Change']}"
    user_prompt += grammar_change_line + "\n"
    user_prompt += "Target:"

    if use_chain_of_thought:
        user_prompt += "\n[Chain-of-thought reasoning or instructions here]" # TODO chain of thought

    # print(user_prompt)
    return user_prompt


def query_llm(client: OpenAI, model_name: str, user_prompt: str):
    system_content = (
        "You are a helpful assistant with expertise in linguistics. "
        "Output only the target sentence in your response with no additional punctuation."
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        n=1
    )
    return response.choices[0].message.content.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Example script that selects training examples by exact/partial overlap, "
                    "generates predictions, calculates metrics (if Target present), and saves results."
    )
    parser.add_argument("train_file", help="Path to the training TSV.")
    parser.add_argument("test_file", help="Path to the test TSV.")
    parser.add_argument("model", help="Model name (gpt-4o, deepseek-chat, deepseek-reasoner).")
    parser.add_argument("--api_key", default=None, help="Optionally provide your OpenAI API key.")
    parser.add_argument("--num_examples", type=int, default=5, help="Max number of examples to include.")
    parser.add_argument("--pos", action="store_true", help="Include part of speech tags in prompt.")
    parser.add_argument("--background", action="store_true", help="Include background info in prompt.")
    parser.add_argument("--descriptive", action="store_true", help="Include extra grammar info in prompt.")
    parser.add_argument("--chain-of-thought", action="store_true", help="Include chain-of-thought reasoning.")
    args = parser.parse_args()

    train_df = pd.read_csv(args.train_file, sep="\t")
    train_df["TagSet"] = train_df["Change"].apply(
        lambda x: set(t.strip() for t in x.split(","))
    )

    train_df.to_csv("testing.csv")

    language = os.path.basename(args.train_file).split("-")[0]

    test_df = pd.read_csv(args.test_file, sep="\t")
    test_df["Hypothesis"] = ""

    base_name = os.path.splitext(os.path.basename(args.test_file))[0]
    flags_used = []
    if args.pos:
        flags_used.append("pos")
    if args.background:
        flags_used.append("background")
    if args.descriptive:
        flags_used.append("descriptive")
    if args.chain_of_thought:
        flags_used.append("chain-of-thought")
    flag_suffix = "_" + "_".join(flags_used) if flags_used else ""
    out_filename = f"{base_name}-{args.model}_ex{args.num_examples}{flag_suffix}.tsv"

    if args.model in ['deepseek-chat', 'deepseek-reasoner']:
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    elif args.model in ['gpt-4o']:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    # loop over each row in test set, build prompt, query LLM, store Hypothesis column
    for idx, row in tqdm(test_df.iterrows(), total=len(test_df)):
        selected_examples = select_examples(train_df, row, max_examples=args.num_examples)
        test_example = {
            "Source": row["Source"],
            "Change": row["Change"],
            "Target": row.get("Target", ""),  # might be empty if no target is present
            "Source-Tagged": row.get("Source-Tagged", "")
        }

        # build prompt
        prompt = build_prompt(
            language=language,
            examples=selected_examples,
            test_example=test_example,
            use_pos=args.pos,
            use_background=args.background,
            use_descriptive=args.descriptive,
            use_chain_of_thought=args.chain_of_thought
        )

        # print the prompt for just the first example to check it looks good
        if idx==1:
            print(prompt)

        # query llm & store hypothesis
        response = query_llm(client, args.model, prompt)
        test_df.at[idx, "Hypothesis"] = response

    # for dev: calculate metrics if Target column is present
    if "Target" in test_df.columns:
        exact_matches = (test_df["Target"] == test_df["Hypothesis"]).sum()
        accuracy = exact_matches / len(test_df)
        print(f"Accuracy: {accuracy*100:.2f}%")

        refs = test_df["Target"].tolist()
        hyps = test_df["Hypothesis"].tolist()
        bleu_score = bleu.corpus_score(hyps, [refs])
        chrf_score = chrf.corpus_score(hyps, [refs])
        print(f"BLEU: {bleu_score}")
        print(f"CHRF: {chrf_score}")

    test_df.to_csv(out_filename, sep="\t", index=False)
    print(f"Predictions saved to: {out_filename}")


if __name__ == "__main__":
    main()

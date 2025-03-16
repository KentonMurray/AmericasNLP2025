import argparse
import requests
import json
import os
import re
import pandas as pd
import sacrebleu

parser = argparse.ArgumentParser(description="Process a language for NLP task.")
parser.add_argument("--language", type=str, required=True, help="Specify the language (e.g., bribri, nahuatl, etc.)")
parser.add_argument("--type1", type=str, required=True, help="Specify the dev,train or test set")
parser.add_argument("--data_path", type=str, required=True, help=" example /export/c09/lavanya/americasNLP/data/")

args = parser.parse_args()
language = args.language  
type1 = args.type1
data_path = args.data_path
openai_api_key = ""
if openai_api_key is None:
    raise ValueError("OpenAI API key is not set in environment variables.")

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

file_path = os.path.join(data_path, f"{language}-{type1}.tsv")  

if not os.path.exists(file_path):
    raise FileNotFoundError(f"File {file_path} not found!")

df = pd.read_csv(file_path, delimiter="\t")
print(df.head())

def process_row(row):
    cot_prompt = f"""
    You are a helpful assistant that generates a new sentence based on the given change, step by step, using Chain of Thought reasoning.
    1. Language used is "{language}".
    2. Understand the Source Sentence:
    - Source Sentence: "{row['Source']}"
    3. Identify the Change:
    - Change to Apply: "{row['Change']}"
    4. Apply the Change. 
    5. The last line should be formatted exactly as follows:
    **PREDICTED TARGET: [your generated sentence]**
    """

    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates new sentences based on the change given step by step using Chain of Thought."},
            {"role": "user", "content": cot_prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 600
    }

    response = requests.post(url, headers=headers, json=data)
    response_content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    print(response_content)
    predicted_match = re.search(r'predicted target:\s*(.*)', response_content, re.IGNORECASE)
    predicted_target = predicted_match.group(1).strip(' "*') if predicted_match else response_content.strip()
    print(predicted_target)
    return {
        "ID": row['ID'],
        "Source": row['Source'],
        "Change": row['Change'],
        "Target": row['Target'].strip(),
        "Predicted Target": predicted_target,
    }


results = df.apply(process_row, axis=1)
results_df = pd.DataFrame(results.tolist())
references = [[target] for target in results_df["Target"].tolist()]
hypotheses = results_df["Predicted Target"].tolist()
corpus_bleu_score = sacrebleu.corpus_bleu(hypotheses, references).score
corpus_chrf_score = sacrebleu.corpus_chrf(hypotheses, references).score

print("Corpus-Level BLEU Score:", round(corpus_bleu_score, 4))
print("Corpus-Level CHRF Score:", round(corpus_chrf_score, 4))

print("Saving results to TSV...")
results_df.to_csv(f"/export/c09/lavanya/americasNLP/cot/train/gpt4/results_{language}.tsv", sep='\t', index=False)
print("Results saved successfully!")

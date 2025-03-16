import argparse
import requests
import json
import os
import re
import pandas as pd
import sacrebleu
from openai import OpenAI

parser = argparse.ArgumentParser(description="Process a language for NLP task.")
parser.add_argument("--language", type=str, required=True, help="Specify the language (e.g., bribri, nahuatl, etc.)")
parser.add_argument("--type1", type=str, required=True, help="Specify the dev,train or test set")
parser.add_argument("--data_path", type=str, required=True, help=" example /export/c09/lavanya/americasNLP/data/")
parser.add_argument("--test_mode", action="store_true", help="Run in test mode with only 5 rows")

args = parser.parse_args()
language = args.language  
type1 = args.type1
data_path = args.data_path
test_mode = args.test_mode

# DeepSeek API key
deepseek_api_key = "sk-"

if deepseek_api_key is None:
    raise ValueError("DeepSeek API key is not set in environment variables.")

# Initialize the DeepSeek client
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

file_path = os.path.join(data_path, f"{language}-{type1}.tsv")  
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File {file_path} not found!")

df = pd.read_csv(file_path, delimiter="\t")

# Limit to first 5 rows if in test mode
if test_mode:
    df = df.head(5)
    print("TEST MODE: Processing only first 5 rows")
else:
    print(f"Processing all {len(df)} rows")

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

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates new sentences based on the change given step by step using Chain of Thought."},
                {"role": "user", "content": cot_prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )
        
        response_content = response.choices[0].message.content
       
        predicted_match = re.search(r'predicted target:\s*(.*)', response_content, re.IGNORECASE)
        predicted_target = predicted_match.group(1).strip(' "*') if predicted_match else response_content.strip()
       
        
        return {
            "ID": row['ID'],
            "Source": row['Source'],
            "Change": row['Change'],
            "Target": row['Target'].strip(),
            "Predicted Target": predicted_target,
        }
    except Exception as e:
        print(f"Error processing row {row['ID']}: {e}")
        return {
            "ID": row['ID'],
            "Source": row['Source'],
            "Change": row['Change'],
            "Target": row['Target'].strip(),
            "Predicted Target": "Error: Failed to generate prediction",
        }

results = df.apply(process_row, axis=1)
results_df = pd.DataFrame(results.tolist())

references = [[target] for target in results_df["Target"].tolist()]
hypotheses = results_df["Predicted Target"].tolist()

corpus_bleu_score = sacrebleu.corpus_bleu(hypotheses, references).score
corpus_chrf_score = sacrebleu.corpus_chrf(hypotheses, references).score

print("Corpus-Level BLEU Score:", round(corpus_bleu_score, 4))
print("Corpus-Level CHRF Score:", round(corpus_chrf_score, 4))

# Define output path with test_mode indicator
output_dir = "/export/c09/lavanya/americasNLP/cot/train/deepseek"
if test_mode:
    output_file = f"{output_dir}/test_results_{language}_5rows.tsv"
else:
    output_file = f"{output_dir}/results_{language}.tsv"

# Save the results to a TSV file
print(f"Saving results to {output_file}...")
results_df.to_csv(output_file, sep='\t', index=False)
print("Results saved successfully!")

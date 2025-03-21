import argparse
import requests
import json
import os
import re
import pandas as pd
import sacrebleu
from tqdm import tqdm
from openai import OpenAI

parser = argparse.ArgumentParser(description="Process a language for NLP task.")
parser.add_argument("--language", type=str, required=True, help="Specify the language (e.g., bribri, nahuatl, etc.)")
parser.add_argument("--type1", type=str, required=True, help="Specify the dev,train or test set")
parser.add_argument("--data_path", type=str, required=True, help=" example /export/c09/lavanya/americasNLP/data/")
parser.add_argument("--n_examples", type=int, default=25, help="Number of few-shot examples to use")

args = parser.parse_args()
language = args.language  
type1 = args.type1
data_path = args.data_path
n_examples = args.n_examples


# DeepSeek API key
deepseek_api_key = ""
if deepseek_api_key is None:
    raise ValueError("DeepSeek API key is not set in environment variables.")
# Initialize the DeepSeek client
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")


file_path = os.path.join(data_path, f"{language}-{type1}.tsv")
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File {file_path} not found!")

df = pd.read_csv(file_path, delimiter="\t")
print(f"Loaded {type1} data with shape: {df.shape}")


train_file_path = os.path.join(data_path, f"{language}-train.tsv")
if not os.path.exists(train_file_path):
    raise FileNotFoundError(f"Training file {train_file_path} not found!")

train_df = pd.read_csv(train_file_path, delimiter="\t")
print(f"Loaded training data with shape: {train_df.shape}")

def count_overlapping_elements(change1, change2):
    """Count overlapping elements between two change descriptions"""
    set_change1 = set(change1.split(","))
    set_change2 = set(change2.split(","))
    return len(set_change1.intersection(set_change2))

def get_few_shot_examples(current_change, n_examples=25):
    """Get few-shot examples most similar to the current change"""

    train_df['overlap_count'] = train_df['Change'].apply(
        lambda x: count_overlapping_elements(x, current_change)
    )

    examples_df = train_df[train_df['overlap_count'] > 0].sort_values(
        by='overlap_count', ascending=False
    )
    

    if len(examples_df) == 0:
        examples_df = train_df.sample(n=min(n_examples, len(train_df)))
    

    return examples_df.head(n_examples)

def create_few_shot_cot_prompt(row, examples_df):
    """Create a few-shot Chain of Thought prompt with examples"""
    system_message = "You are a helpful assistant that generates a new sentence based on the given change, using Chain of Thought reasoning."
    

    few_shot_examples = []
    for _, example in examples_df.iterrows():
        user_example = f"""
        Source Sentence: "{example['Source']}"
        Change to Apply: "{example['Change']}"
        """
        
        assistant_example = f"""
        Let me analyze this step by step:
        
        1. I need to understand the source sentence: "{example['Source']}"
        2. I need to apply the change: "{example['Change']}"
        3. Analyzing the grammatical transformation required...
        4. Making the necessary changes to the sentence...
        
        **PREDICTED TARGET: {example['Target']}**
        """
        
        few_shot_examples.append({"role": "user", "content": user_example})
        few_shot_examples.append({"role": "assistant", "content": assistant_example})
    

    test_prompt = f"""
    Source Sentence: "{row['Source']}"
    Change to Apply: "{row['Change']}"
    
    Follow the same Chain of Thought process as in the examples, and then provide your prediction.
    The last line should be formatted exactly as follows:
    **PREDICTED TARGET: [your generated sentence]**
    """
    

    messages = [
        {"role": "system", "content": system_message}
    ] + few_shot_examples + [
        {"role": "user", "content": test_prompt}
    ]
    
    return messages

def process_row(row):

    examples_df = get_few_shot_examples(row['Change'], n_examples)
    messages = create_few_shot_cot_prompt(row, examples_df)
    response = client.chat.completions.create(
            model="deepseek-chat",
            messages= messages,
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
        "Num Examples": len(examples_df)
    }

print(f"Processing {len(df)} rows with {n_examples} few-shot examples per row...")
results = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    result = process_row(row)
    results.append(result)

results_df = pd.DataFrame(results)
references = [[target] for target in results_df["Target"].tolist()]
hypotheses = results_df["Predicted Target"].tolist()
corpus_bleu_score = sacrebleu.corpus_bleu(hypotheses, references).score
corpus_chrf_score = sacrebleu.corpus_chrf(hypotheses, references).score
print("Corpus-Level BLEU Score:", round(corpus_bleu_score, 4))
print("Corpus-Level CHRF Score:", round(corpus_chrf_score, 4))
exact_matches = sum(1 for h, r in zip(hypotheses, [ref[0] for ref in references]) if h == r)
accuracy = (exact_matches / len(hypotheses)) * 100
print(f"Exact Match Accuracy: {accuracy:.2f}%")
print("Saving results to TSV...")
output_path = f"/export/c09/lavanya/americasNLP/cot/train/deepseek/fewshot_results_25_{language}.tsv"
results_df.to_csv(output_path, sep='\t', index=False)
print(f"Results saved successfully to {output_path}!")

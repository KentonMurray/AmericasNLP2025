import sys
import pandas as pd
import sacrebleu

def calculate_scores(predicted, target):
    bleu_score = sacrebleu.corpus_bleu(predicted, [target]).score
    chrf_score = sacrebleu.corpus_chrf(predicted, [target]).score
    return bleu_score, chrf_score

def calc_acc(predicted, target):
    total = len(target)
    correct = sum(1 for p, t in zip(predicted, target) if p == t)
    return correct / total if total > 0 else 0.0

def main(tsv_file):
    df = pd.read_csv(tsv_file, sep='\t')

    predicted = list(df["Hypothesis"].astype(str))
    target = list(df["Target"].astype(str))

    accuracy = calc_acc(predicted, target)
    print("Exact Match Accuracy: {:.2f}%".format(accuracy * 100))

    bleu, chrf = calculate_scores(predicted, target)
    print("BLEU: {:.2f}".format(bleu))
    print("ChrF: {:.2f}".format(chrf))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file.tsv>")
        sys.exit(1)
    tsv_file = sys.argv[1]
    main(tsv_file)

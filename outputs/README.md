This folder contain outputs from running other teams' systems or the GPT-4 components of their systems.

Outputs are generated using GPT-4o rather than GPT-4.

Additional post-processing is done to each output to remove final punctuation when it appears.

### Dev metrics:

|                                   | ---      | Bribri   | ---      |   | ---      | Maya     | ---      |   | ---      | Guarani  | ---      |   | ---      | Nahuatl  | ---      |
|-----------------------------------|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|
|                                   | **Acc.** | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |
| Giving it a Shot                  | 14.62    | 40.19    | 61.27    |   | 51.01    | 76.49    | 90.82    |   | 41.77    | 47.34    | 85.98    |   | 1.14     | 0.78     | 31.74    |
| Giving it a Shot (post-processed) | 14.62    | 40.30    | 61.27    |   | 51.01    | 76.75    | 90.83    |   | 43.04    | 49.87    | 86.05    |   | 1.14     | 0.80     | 31.77    |
| Meenzer (only GPT component)      | 10.85    | 38.98    | 61.86    |   | 51.68    | 75.84    | 89.94    |   | 45.57    | 53.65    | 86.00    |   | 1.70     | 4.31     | 43.17    |
| Meenzer (post-processed)          | 10.85    | 39.19    | 61.87    |   | 51.68    | 75.84    | 89.94    |   | 45.57    | 54.16    | 86.01    |   | 1.70     | 4.31     | 43.17    |


### System info
**Giving it a Shot** includes training examples formatted as a csv completion task. Predictions are generated using temperature=0.\
Examples used in the prompt are selected as follows:
- If there are at least 10 exact matches of the Change tag in the training data, select the top 10, sorted in descending order by sum of BLEU + chrF match with the dev/test example
- If there are less than 3 exact matches (e.g., in cases where multiple changes occur), then a backoff method is used. This splits the Change tag into its component feature, then for each component feature:
  - If there is at least 1 exact match, add the top (up to) 3 training examples to the prompt sorted by BLEU + chrF
  - If there are no exact matches, add the top non-exact match that contains the component feature
  - Finally, add the top (up to) 8 training examples that include some combination of the component features


**Meenzer** includes up to 20 training examples in the form of a chat history, and includes the target language in the prompt.\
Training examples are selected based on having at least one overlapping component change, and sorted in descending order of overlapping component changes (i.e., the training example with the highest number of overlapping changes to the test example is at the top).\
Predictions are generated with temperature=0.


### Links to system descriptions & code:
Giving it a Shot:\
[The unreasonable effectiveness of large language models for low-resource clause-level morphology: In-context generalization or prior exposure?](https://aclanthology.org/2024.americasnlp-1.20.pdf) \
GitHub: https://github.com/ColemanHaley/GivingItAShot/tree/main

Meenzer:\
[JGU Mainz’s Submission to the AmericasNLP 2024 Shared Task on the Creation of Educational Materials for Indigenous Languages
](https://aclanthology.org/2024.americasnlp-1.23/)\
GitHub: https://github.com/MinhDucBui/SharedTaskAmericasNLP2024/tree/main/ChatGPT
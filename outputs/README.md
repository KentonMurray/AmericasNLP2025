This folder contains results from running variations of our systems as well as other teams' systems or the GPT-4 components of their systems.
We tested variations of the GPT-4 component of Teams Giving it a Shot (Haley, AmericasNLP 2024) and Meenzer (Bui & von der Wense, AmericasNLP 2024) for comparison benchmarks while devloping our system.


### Dev metrics:
#### Our system, gpt4-o

|                           | ---      | Bribri   | ---      |   | ---      | Maya     | ---      |   | ---      | Guarani  | ---      |   | ---      | Nahuatl  | ---      |
|---------------------------|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|
|                           | **Acc.** | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |
| Base prompt, 3 examples   | 16.98    | 44.52    | 62.89    |   | 54.36    | 77.37    | 90.84    |   | 39.24    | 47.44    | 85.39    |   | 1.14     | 4.86     | 34.98    |
| Base prompt, 5 examples   | 17.92    | 44.49    | 63.87    |   | 55.03    | 76.67    | 90.43    |   | 41.77    | 49.75    | 85.97    |   | 1.14     | 5.41     | 37.52    |
| Base prompt, 10 examples  | 18.40    | 45.96    | 65.13    |   | 54.36    | 76.39    | 90.41    |   | 39.24    | 49.24    | 84.70    |   | 1.14     | 6.38     | 38.88    |
| Base prompt, 20 examples  | 15.57    | 44.76    | 64.75    |   | 58.39    | 78.64    | 90.98    |   | 40.51    | 54.51    | 86.17    |   | 1.14     | 5.71     | 39.19    |
| POS, 3 examples           |          |          |          |   | 53.02    | 76.24    | 89.16    |   | 39.24    | 56.78    | 85.40    |   |          |          |          |
| POS, 5 examples           |          |          |          |   | 48.32    | 72.51    | 88.75    |   | 41.77    | 55.96    | 85.12    |   |          |          |          |
| POS, 10 examples          |          |          |          |   | 55.70    | 76.49    | 90.44    |   | 44.30    | 52.37    | 86.15    |   |          |          |          |
| POS, 20 examples          |          |          |          |   | 56.38    | 77.24    | 90.36    |   | 41.77    | 51.77    | 86.27    |   |          |          |          |
| Grammar info, 10 examples | 16.98    | 45.63    | 65.86    |   | 54.36    | 76.92    | 90.79    |   | 43.04    | 55.15    | 86.95    |   |          |          |          |

#### Our system, deepseek-chat
|                          | ---      | Bribri   | ---      |   | ---      | Maya     | ---      |   | ---      | Guarani  | ---      |   | ---      | Nahuatl  | ---      |
|--------------------------|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|
|                          | **Acc.** | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |
| Base prompt, 5 examples  |  17.92   |    46.24 |   65.75  |   |55.03     |76.96     |   90.61  |   | 44.30    | 52.88    | 87.01    |   | 2.27     |   6.03   |40.84     |
| Base prompt, 10 examples | 18.40    | 45.79    |  66.69   |   |    55.70 |    77.31 | 91.31    |   | 44.30    | 55.63    | 87.18    |   | 2.27     |8.13      | 42.58    |
| Base prompt, 20 examples |  18.87   |   47.68  | 67.43    |   |  56.38   |   78.20  |  91.49   |   | 44.30    | 54.02    | 87.42    |   |5.11      |  8.88    | 43.56    |
| POS, 10 examples         |          |          |          |   |          |          |          |   | 41.77    | 51.59    | 86.45    |   |          |          |          |


####Other teams

### Dev metrics:

|                                                             | ---      | Bribri   | ---      |   | ---      | Maya     | ---      |   | ---      | Guarani  | ---      |   | ---      | Nahuatl  | ---      |
|-------------------------------------------------------------|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|---|----------|----------|----------|
|                                                             | **Acc.** | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |   | **Acc**. | **BLEU** | **chrF** |
| Giving it a Shot                                            | 15.57    | 40.50    | 61.96    |   | 52.35    | 76.48    | 90.98    |   | 43.04    | 49.80    | 86.39    |   | 2.27     | 2.72     | 36.57    |
| Giving it a Shot (remove ".")                               | 15.57    | 40.81    | 61.97    |   | 52.35    | 76.61    | 90.99    |   | 45.57    | 52.97    | 86.47    |   |          |          |          |
| Giving it a Shot (20 examples, remove ".")                  | 14.62    | 40.43    | 61.50    |   | 55.70    | 77.47    | 90.99    |   | 44.30    | 52.41    | 85.81    |   |          |          |          |
| Giving it a Shot (Meenzer sorting, 20 examples)             |          |          |          |   |          |          |          |   | 41.77    | 50.18    | 85.34    |   |          |          |          |
| Giving it a Shot (Meenzer sorting, 10 examples)             |          |          |          |   |          |          |          |   | 43.04    | 47.82    | 84.76    |   |          |          |          |
| Giving it a Shot (Meenzer sorting, 10 examples, remove ".") | 9.43     | 26.01    | 53.12    |   | 35.57    | 65.10    | 86.10    |   | 44.30    | 50.81    | 84.86    |   | 1.70     | 1.08     | 35.66    |
| Meenzer                                                     | 10.85    | 38.98    | 61.86    |   | 51.68    | 75.84    | 89.94    |   | 45.57    | 53.65    | 86.00    |   | 1.70     | 4.31     | 43.17    |
| Meenzer (remove ".")                                        | 10.85    | 39.19    | 61.87    |   | 51.68    | 75.84    | 89.94    |   | 45.57    | 54.16    | 86.01    |   | 1.70     | 4.31     | 43.17    |
| Meenzer (GIS sorting & 10 examples, remove ".")             | 12.26    | 29.54    | 57.19    |   | 51.01    | 75.51    | 90.05    |   | 41.77    | 53.98    | 87.18    |   |          |          |          |
| Meenzer (GIS sorting & 20 examples, remove ".")             | 12.74    | 31.38    | 57.88    |   | 55.70    | 77.56    | 90.40    |   | 41.77    | 51.72    | 85.69    |   |          |          |          |



### System info
**Giving it a Shot** includes training examples formatted as a csv completion task. Predictions are generated using temperature=0, contrastive to 0.1 as reported in (Haley, AmericasNLP 2024).\
Examples used in the prompt are selected as follows:
- If there are at least 3 exact matches of the Change tag in the training data, select the top 10, sorted in descending order by sum of BLEU + chrF match with the dev/test example
- If there are less than 3 exact matches (e.g., in cases where multiple changes occur), then a backoff method is used. This splits the Change tag into its component feature, then for each component feature:
  - If there is at least 1 exact match, add the top (up to) 3 training examples to the prompt sorted by BLEU + chrF
  - If there are no exact matches, add the top non-exact match that contains the component feature
  - Finally, add the top (up to) 8 training examples that include some combination of the component features


**Meenzer** includes up to 20 training examples in the form of a chat history, and includes the target language in the prompt.\
Training examples are selected based on having at least one overlapping component change, and sorted in descending order of overlapping component changes (i.e., the training example with the highest number of overlapping changes to the test example is at the top).\
Predictions are generated with temperature=0.


### Links to system descriptions & code:
Giving it a Shot:\
[The unreasonable effectiveness of large language models for low-resource clause-level morphology: In-context generalization or prior exposure?](https://aclanthology.org/2024.americasnlp-1.20.pdf) (Haley, AmericasNLP 2024)\
GitHub: https://github.com/ColemanHaley/GivingItAShot/tree/main

Meenzer:\
[JGU Mainz’s Submission to the AmericasNLP 2024 Shared Task on the Creation of Educational Materials for Indigenous Languages
](https://aclanthology.org/2024.americasnlp-1.23/) (Bui & von der Wense, AmericasNLP 2024)\
GitHub: https://github.com/MinhDucBui/SharedTaskAmericasNLP2024/tree/main/ChatGPT

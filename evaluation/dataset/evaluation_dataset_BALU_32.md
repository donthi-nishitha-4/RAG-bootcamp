Evaluation dataset: evaluation_dataset_UDAY_32.json

Category distribution (32 queries):

- factual: 13
- multi-hop: 6
- analytical: 2
- summary: 3
- anomaly: 1
- minutes: 1
- correspondence: 1
- out_of_scope (adversarial): 5

Notes:
- Adversarial / out-of-scope queries intentionally cover unrelated domains
  (general knowledge, translation) to test model abstention behavior (~15.6%).
- The dataset mixes contract clauses, NCR/DPR items, correspondence and meeting
  minutes to reflect realistic enterprise RAG workloads.

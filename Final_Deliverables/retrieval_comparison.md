# Retrieval Comparison

| Method | Precision@5 | Notes |
|---|---:|---|
| Naive (Vector Only) | 0.26 | Baseline vector search |
| + Metadata Filtering | 0.26 | Vector + Entity Type filtering |
| Hybrid (BM25 + Vector) | 0.26 | Reciprocal Rank Fusion |
| Hybrid + Cross-Encoder | 0.26 | Retrieve 30 -> Rerank to 5 |
| HyDE | 0.23 | Hypothetical doc embeddings |
| Multi-query | 0.08 | Union of paraphrase retrievals |

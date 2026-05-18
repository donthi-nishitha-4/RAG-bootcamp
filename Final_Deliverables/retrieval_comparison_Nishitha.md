# Retrieval Comparison

| Method | Precision@5 | Latency (ms) | Notes |
|---|---:|---:|---|
| Naive (Vector Only) | 0.26 | - | Baseline vector search |
| + Metadata Filtering | 0.26 | - | Vector + Entity Type filtering |
| Hybrid (BM25 + Vector) | 0.26 | - | Reciprocal Rank Fusion |
| Hybrid + MS-MARCO | 0.26 | 2531 | ms-marco-MiniLM-L-12-v2 |
| Hybrid + BGE Reranker | 0.22 | 8207 | bge-reranker-v2-m3 |
| HyDE | 0.24 | - | Hypothetical doc embeddings |
| Multi-query | 0.07 | - | Union of paraphrase retrievals |
| Contextual Retrieval | 0.39 | - | Document context prepended to chunks |

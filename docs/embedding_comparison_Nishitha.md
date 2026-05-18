# Embedding Model Comparison

| Model | Dim | Latency (ms/doc) | Device |
|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | 7.03 | CPU |
| BAAI/bge-large-en-v1.5 | 1024 | 54.28 | CPU |
| nomic-ai/nomic-embed-text-v1.5 | 768 | 43.74 | CPU |

![UMAP Comparison](images/umap_comparison.png)

## Notes

- Dataset used:
  - `data/dmrc/dmrc_Synthetic_Dataset.json`
- Models compared:
  - `all-MiniLM-L6-v2`
  - `BAAI/bge-large-en-v1.5`
  - `nomic-ai/nomic-embed-text-v1.5`
- UMAP outputs generated:
  - `docs/images/umap_all-MiniLM-L6-v2.png`
  - `docs/images/umap_BAAI_bge-large-en-v1.5.png`
  - `docs/images/umap_nomic-ai_nomic-embed-text-v1.5.png`
  - `docs/images/umap_comparison.png`
- Observations:
  - Compare whether `contract_clause` points form a distinct group from `ncr_description` and `dpr_narrative`.
  - Check if `ncr_description` documents are closer to live incident language and if `dpr_narrative` texts occupy a separate reporting cluster.
  - A good embedding model should separate contract clauses from NCR and DPR narrative styles while keeping metro-rail terminology coherent.
- Metro-rail term separation:
  - Evaluate how well the plots isolate domain terms like `OHE catenary`, `ballastless track`, and `tunnel boring machine` from generic text.
  - In this comparison, `BAAI/bge-large-en-v1.5` appears to give the best domain-term separation, with `nomic-ai/nomic-embed-text-v1.5` also showing stronger clustering than the smaller `all-MiniLM-L6-v2`.
UDAY Plan and Task Distribution

Overview
--------
This document captures the next work items (assigned to UDAY) required to finish the bootcamp deliverables. Files created for this work include experiment templates, evaluation query set placeholders, retrieval/reranker stubs, chunker skeletons, and RAGAS setup notes (all suffixed with _UDAY).

High-level goals
- Expand evaluation queries to 30+ examples across entity types
- Implement two new retrieval strategies: HyDE and multi-query
- Implement cross-encoder reranking comparison and measure CPU latency
- Build NCR and DPR document-type-specific chunkers
- Prepare golden evaluation dataset (30+ QA-context triples)
- Set up RAGAS pipeline with Groq as evaluator
- Fill in missing "Surprising Finding" and "Production Implication" fields in experiment logs

Files created (proof-of-work)
- [docs/UDAY_tasks/experiment_template_UDAY.md](docs/UDAY_tasks/experiment_template_UDAY.md)
- [evaluation/queries_30_UDAY.csv](evaluation/queries_30_UDAY.csv)
- [GOLDEN_dataset/golden_eval_template_UDAY.json](GOLDEN_dataset/golden_eval_template_UDAY.json)
- [scripts/hyde_multiquery_stubs_UDAY.py](scripts/hyde_multiquery_stubs_UDAY.py)
- [scripts/reranker_benchmark_UDAY.py](scripts/reranker_benchmark_UDAY.py)
- [src/chunkers/ncr_dpr_chunker_UDAY.py](src/chunkers/ncr_dpr_chunker_UDAY.py)
- [docs/UDAY_tasks/ragas_setup_UDAY.md](docs/UDAY_tasks/ragas_setup_UDAY.md)
- [docs/UDAY_tasks/proof_of_work_paths_UDAY.md](docs/UDAY_tasks/proof_of_work_paths_UDAY.md)

How to use
- Use the experiment template for every experiment you run; commit one file per experiment to a branch named `uday/<short-task-name>`.
- Replace placeholders in the evaluation CSV and golden dataset with the real queries and expected answers as you build them.
- Use the stub scripts to iterate quickly; they are intentionally lightweight and include TODO markers for implementation detail.

Next steps for UDAY
1. Populate `evaluation/queries_30_UDAY.csv` with 30 queries (mix of contract clauses, NCRs, DPRs, correspondence, minutes).
2. Populate `GOLDEN_dataset/golden_eval_template_UDAY.json` with 30 QA-context triples and expected answers.
3. Implement the HyDE and multi-query retrieval functions in `scripts/hyde_multiquery_stubs_UDAY.py` and run on query set.
4. Implement reranker comparison in `scripts/reranker_benchmark_UDAY.py` and measure Precision@5 + CPU latency.
5. Implement chunkers in `src/chunkers/ncr_dpr_chunker_UDAY.py` and test with `scripts/ingest_data.py` (local runs).
6. Set up RAGAS evaluation with guidance in `docs/UDAY_tasks/ragas_setup_UDAY.md`.

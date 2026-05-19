Proof-of-Work Paths (BALU)

When you've completed the tasks, show the following paths in your submission as proof-of-work. For each item include a brief README or experiment file.

- Expanded query set: [evaluation/queries_30_UDAY.csv](evaluation/queries_30_UDAY.csv)
- Golden eval triples: [GOLDEN_dataset/golden_eval_template_UDAY.json](GOLDEN_dataset/golden_eval_template_UDAY.json)
- Experiment logs (one per experiment): `experiments/BALU-<id>_UDAY.md`
- HyDE/multi-query code: [scripts/hyde_multiquery_stubs_UDAY.py](scripts/hyde_multiquery_stubs_UDAY.py)
- Reranker benchmark: [scripts/reranker_benchmark_UDAY.py](scripts/reranker_benchmark_UDAY.py)
- NCR/DPR chunkers: [src/chunkers/ncr_dpr_chunker_UDAY.py](src/chunkers/ncr_dpr_chunker_UDAY.py)
- RAGAS setup notes: [docs/UDAY_tasks/ragas_setup_UDAY.md](docs/UDAY_tasks/ragas_setup_UDAY.md)

Commit & branch guidance
- Create branch `BALU/<task-short-name>` for each major item. Example: `BALU/queries-30`
- Include small README or brief run instructions in each branch root describing how to reproduce results.


RAGAS Evaluation Pipeline Setup (BALU)

Goal: configure and run the RAGAS automated evaluation pipeline using Groq as the evaluation LLM.

Steps (high-level)
1. Ensure Groq access and API key in `.env` as `GROQ_API_KEY`.
2. Install RAGAS dependencies (see requirements or create isolated venv).
3. Prepare the golden dataset at `GOLDEN_dataset/golden_eval_template_UDAY.json` with 30 triples.
4. Configure RAGAS to load queries from the `evaluation/queries_30_UDAY.csv` or golden dataset.
5. Run RAGAS evaluation and collect metrics (Exact Match, F1, RAGAS-specific metrics).

Notes
- If Groq is unavailable, fallback to OpenAI or a local LLM for development runs.
- Record the `Surprising Finding` and `Production Implication` fields in experiment logs for every run.


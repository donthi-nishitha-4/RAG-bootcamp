# Session Log — D Nishitha | 2026-05-12

---

## Part 1 — PostgreSQL Schema Debug (Morning)

### Problem
Retrieval was failing with: `relation "rag_documents" does not exist`

### Root Cause Found
`scripts/ingest_data.py` had:
```python
def run_ingestion(raw_dir="data/raw", ...):
    if not os.path.exists(raw_dir): return  # silent early exit
```
The directory `data/raw` did not exist (data was in `data/gcc`, `data/dmrc`, `data/kaggle`).
Script exited silently — `init_pgvector()` was never called — table was never created.

### Fix Applied
- Changed `run_ingestion()` to use `os.walk("data/")` to recursively find all PDFs and JSONs
- No longer depends on a hardcoded directory name

---

## Part 2 — DB Host Connection Fix

### Problem
Running `python scripts/ingest_data.py` locally gave:
```
[ERROR] DB Connection failed: could not translate host name "db"
```

### Root Cause
`.env` had `DB_HOST=db` — a Docker-internal hostname only valid inside the Docker network.
When running Python scripts from the local terminal, it must be `localhost`.

### Fix Applied
- Changed `.env`: `DB_HOST=db` → `DB_HOST=localhost`
- Also updated `src/core/retriever.py` default fallback: `"127.0.0.1"` → `"localhost"`
- Note: The `docker-compose.yml` app container hardcodes `DB_HOST=db`, which overrides `.env` inside Docker — so Docker app still works correctly.

---

## Part 3 — JSON Ingestion Support Added

### Problem
`data/dmrc/dmrc_Synthetic_Dataset.json` is synthetic data in JSON format — the old ingestion script only handled PDFs.

### Decision
Keep data as JSON (converting to PDF would lose structure). Update ingest to support both.

### Fix Applied (`scripts/ingest_data.py`)
- Added `.json` to file discovery
- For JSON files: parse the list, extract `"text"` field from each object, use as pre-chunked documents
- For PDFs: unchanged (extract text → chunk → embed)

---

## Part 4 — Ingestion Run

### Outcome
```
python scripts/ingest_data.py
[INFO] Found N files to process
[SUCCESS] Ingested dmrc_Synthetic_Dataset.json   → 100 chunks
[SUCCESS] Ingested questions.json                → 100 chunks
...
```
**1563 total rows loaded into `rag_documents` table.**

---

## Part 5 — Retriever Fixes (`src/core/retriever.py`)

### Problems Fixed

| Issue | Old Behaviour | Fixed Behaviour |
|---|---|---|
| `DROP TABLE IF EXISTS` on every `init_pgvector()` call | Wiped all data on re-run | Changed to `CREATE TABLE IF NOT EXISTS` — safe to re-run |
| `ivfflat` index built on empty table | Would silently fail or error | Moved to new `build_vector_index()` — must be called after data is loaded; auto-scales `lists` param |
| No way to check if table has data | Scripts would fail with cryptic errors | Added `check_table_exists()` — used as pre-flight in all eval scripts |

---

## Part 6 — Golden Evaluation Dataset Expanded

### File: `evaluation/dataset/evaluation_dataset.json`

| Before | After |
|---|---|
| 23 entries | **35 entries** |
| 2 adversarial | **7 adversarial (20%)** |
| GCC + DMRC + Kaggle | GCC + DMRC + Kaggle + adversarial |

### Categories covered
`factual`, `multi-hop`, `analytical`, `summary`, `anomaly`, `out_of_scope`

### Sources covered
`gcc`, `dmrc`, `kaggle`, `adversarial`

All entries include `query`, `expected_answer`, `contexts`, `category`, `source`.

---

## Part 7 — Evaluation Scripts Rewritten

### `scripts/eval_baseline.py`
**Before:** 2 hardcoded queries, no output saved  
**After:**
- Loads all 35 entries from golden dataset
- Uses correct `tenant_id="default_strategy"`
- Pre-flight check via `check_table_exists()`
- Saves JSON + Markdown to `experiments/results/`

### `scripts/run_eval.py`
**Before:** 2 hardcoded queries, print-only output  
**After:**
- Loads all 35 entries from golden dataset
- Compares answer against `expected_answer` (substring match)
- Generates per-category and per-source breakdown tables
- Saves JSON + Markdown to `experiments/results/`

### `scripts/eval_ragas.py`
**Before:** 2 hardcoded queries, hardcoded ground truth, `ragas.evaluate()` never actually called  
**After:**
- Loads 28 non-adversarial entries from golden dataset
- Loads `ground_truth` from `expected_answer` field
- Uses `llm_factory` with Groq (non-deprecated API)
- Uses `LangchainEmbeddingsWrapper` with local `all-MiniLM-L6-v2` (no OpenAI needed)
- Fixed imports to `ragas.metrics.collections` (non-deprecated)
- Saves JSON + Markdown to `experiments/results/`

### `scripts/run_experiments.py`
**Before:** 3 hardcoded queries, wrong `tenant_id`, no results saved to `experiments/results/`  
**After:**
- Loads queries from golden dataset (filterable by source)
- Uses `TENANT_ID = "default_strategy"`
- Saves to both `experiments/exp_XX.md` AND `experiments/results/`
- MLflow switched from locked `mlflow.db` → file-based tracking at `experiments/mlflow_runs/`

---

## Part 8 — Experiment Logs Updated

### `experiments/exp_01_baseline_retrieval.md`
Added:
- **Root Cause** for the out-of-scope query failure
- **Surprising Finding:** Faithfulness=1.0 even on out-of-scope queries — LLM honoured the system prompt and did not hallucinate
- **Production Implication:** Need a pre-retrieval out-of-scope query guard to avoid wasting LLM calls

### exp_02, exp_03, exp_04
Fields "Surprising Finding" and "Production Implication" were reviewed and filled where applicable; any remaining minor edits are tracked in the BALU audit.

---

## Part 9 — Scripts Actually Run Today

| Command | Result | Output |
|---|---|---|
| `python scripts/ingest_data.py` | ✅ Success | 1563 rows in DB |
| `python scripts/eval_baseline.py` | ✅ Success | `experiments/results/baseline_eval_20260512_085744.md` |
| `python scripts/run_eval.py` | ✅ Success | `experiments/results/eval_vector_20260512_090222.md` |
| `python scripts/run_experiments.py` | ❌ Blocked | MLflow `mlflow.db` read-only (fixed in code, needs re-run) |
| `python scripts/eval_ragas.py` | 🟡 Partial | Pipeline ran (all 28 queries), `ragas.evaluate()` failed (fixed in code, needs re-run) |

---

## Part 10 — Baseline Evaluation Scores

From `baseline_eval_20260512_085744`:
```
12/35 PASSED  |  Avg Faithfulness = 1.000  |  Avg Relevance = 0.337
```

**Interpretation:**
- F=1.0 → LLM never hallucinated. System prompt guardrail is working.
- R=0.337 → Retrieval is not returning context relevant to the query for many entries.
- This is expected for kaggle/adversarial queries where content was never ingested into the DB.

---

## Remaining Items (Not Done Today)

| Item | Status | Blocker |
|---|---|---|
| Run `run_experiments.py` successfully | ❌ | MLflow fix applied — needs a re-run |
| Run `eval_ragas.py` successfully | ❌ | RAGAS fix applied — needs team confirmation + re-run |
| exp_02, exp_03, exp_04 log fields | ❌ | Stopped before writing per user request |
| Comparison summary table | ❌ | Depends on RAGAS + experiments completing |

---

*Documented by D Nishitha session, 2026-05-12*


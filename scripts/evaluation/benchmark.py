"""
run_eval.py — D Nishitha's Evaluation Runner
Loads the 30+ golden evaluation dataset and runs all queries through the RAG pipeline.
Results are saved to experiments/results/ as JSON + Markdown summary.
Covers: faithfulness, relevance, expected_answer comparison, per-category breakdown.
"""
import sys
import os
import json
import datetime

# Add project root to path

from src.core.pipeline import ask_rag
from src.evals.metrics import evaluate_generation

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results')
TENANT_ID    = "default_strategy"   # tenant used during ingestion


def load_dataset(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_eval(dataset, search_type="vector"):
    results = []
    print(f"\n[INFO] Running evaluation — {len(dataset)} queries | search_type={search_type} | tenant={TENANT_ID}")

    for i, item in enumerate(dataset, start=1):
        query           = item.get("query", "").strip()
        expected_answer = item.get("expected_answer", "")
        category        = item.get("category", "unknown")
        source          = item.get("source", "unknown")

        if not query:
            continue

        print(f"\n[{i}/{len(dataset)}] [{source}|{category}] {query}")

        # --- RAG pipeline ---
        rag_result = ask_rag(query, tenant_id=TENANT_ID, search_type=search_type)
        answer  = rag_result.get("answer", "")
        context = rag_result.get("context", "")
        retrieved_chunks = rag_result.get("retrieved_chunks", [])

        # --- Metric scoring ---
        scores = evaluate_generation(query, context, answer)
        faithfulness = scores.get("faithfulness", 0.0)
        relevance    = scores.get("relevance",    0.0)
        eval_error   = scores.get("error")

        # --- Expected-answer match (simple substring check) ---
        expected_match = (
            expected_answer.lower() in answer.lower()
            if expected_answer and "Not found in context" not in expected_answer
            else None   # adversarial — skip match check
        )

        status = "PASSED" if (not eval_error and faithfulness >= 0.7 and relevance >= 0.7) else "FAILED"

        print(f"   -> {status}  F={faithfulness:.2f}  R={relevance:.2f}  expected_match={expected_match}")
        if eval_error:
            print(f"   [WARN] Eval error: {eval_error}")

        results.append({
            "query":          query,
            "category":       category,
            "source":         source,
            "answer":         answer,
            "context":        context,
            "retrieved_chunks": retrieved_chunks,
            "expected_answer":expected_answer,
            "expected_match": expected_match,
            "faithfulness":   faithfulness,
            "relevance":      relevance,
            "eval_error":     eval_error,
            "status":         status,
            "search_type":    search_type,
        })

    return results


def save_results(results, search_type):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    slug      = f"eval_{search_type}_{timestamp}"

    # --- JSON output ---
    json_path = os.path.join(RESULTS_DIR, f"{slug}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] JSON  → {json_path}")

    # --- Markdown summary ---
    total   = len(results)
    passed  = sum(1 for r in results if r["status"] == "PASSED")
    failed  = total - passed
    avg_f   = sum(r["faithfulness"] for r in results) / total if total else 0
    avg_r   = sum(r["relevance"]    for r in results) / total if total else 0

    # Per-category breakdown
    categories = sorted(set(r["category"] for r in results))
    cat_rows = ""
    for cat in categories:
        cat_items = [r for r in results if r["category"] == cat]
        c_pass = sum(1 for r in cat_items if r["status"] == "PASSED")
        c_f    = sum(r["faithfulness"] for r in cat_items) / len(cat_items)
        c_r    = sum(r["relevance"]    for r in cat_items) / len(cat_items)
        cat_rows += f"| {cat} | {len(cat_items)} | {c_pass} | {c_f:.2f} | {c_r:.2f} |\n"

    # Per-source breakdown
    sources = sorted(set(r["source"] for r in results))
    src_rows = ""
    for src in sources:
        src_items = [r for r in results if r["source"] == src]
        s_pass = sum(1 for r in src_items if r["status"] == "PASSED")
        s_f    = sum(r["faithfulness"] for r in src_items) / len(src_items)
        s_r    = sum(r["relevance"]    for r in src_items) / len(src_items)
        src_rows += f"| {src} | {len(src_items)} | {s_pass} | {s_f:.2f} | {s_r:.2f} |\n"

    # Query-level table
    query_rows = ""
    for r in results:
        match_str = "✅" if r["expected_match"] is True else ("N/A" if r["expected_match"] is None else "❌")
        query_rows += (
            f"| {r['source']} | {r['category']} | {r['query'][:60]}… | "
            f"{r['faithfulness']:.2f} | {r['relevance']:.2f} | {match_str} | {r['status']} |\n"
        )

    md = f"""# Evaluation Results — {search_type.upper()} search
**Run:** {timestamp}  |  **Tenant:** {TENANT_ID}  |  **Dataset:** evaluation_dataset.json

## Overall Summary
| Metric | Value |
|---|---|
| Total Queries | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Pass Rate | {passed/total*100:.1f}% |
| Avg Faithfulness | {avg_f:.3f} |
| Avg Relevance | {avg_r:.3f} |

## Breakdown by Category
| Category | Count | Passed | Avg Faithfulness | Avg Relevance |
|---|---|---|---|---|
{cat_rows}
## Breakdown by Source
| Source | Count | Passed | Avg Faithfulness | Avg Relevance |
|---|---|---|---|---|
{src_rows}
## Per-Query Results
| Source | Category | Query | Faithfulness | Relevance | Expected Match | Status |
|---|---|---|---|---|---|---|
{query_rows}
---
*Generated by run_eval.py — D Nishitha*
"""

    md_path = os.path.join(RESULTS_DIR, f"{slug}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"[SAVED] Markdown → {md_path}")
    return json_path, md_path


if __name__ == "__main__":
    dataset = load_dataset(DATASET_PATH)
    print(f"[INFO] Loaded {len(dataset)} entries from golden dataset.")

    # Run vector search evaluation
    vector_results = run_eval(dataset, search_type="vector")
    save_results(vector_results, search_type="vector")

    # Run hybrid search evaluation
    hybrid_results = run_eval(dataset, search_type="hybrid")
    save_results(hybrid_results, search_type="hybrid")

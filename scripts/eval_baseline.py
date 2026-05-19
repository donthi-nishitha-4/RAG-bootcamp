"""
eval_baseline.py — Sanity-check baseline evaluation (D Nishitha)
Runs the full 30+ golden dataset through the pipeline using your LLM-based metrics.
Results saved to experiments/results/.
This is a quick smoke-test to confirm the pipeline is working before running RAGAS.
"""
import sys
import os
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import ask_rag
from src.evals.metrics import evaluate_generation
from src.core.retriever import check_table_exists

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results')
TENANT_ID    = "default_strategy"


def run_baseline_eval():
    # Pre-flight check
    if not check_table_exists():
        print("[ERROR] rag_documents table is empty or missing. Run: python scripts/ingest_data.py")
        return

    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    print(f"[INFO] Loaded {len(dataset)} queries. Running baseline evaluation...\n")

    records = []
    passed = failed = 0

    for i, item in enumerate(dataset, 1):
        query    = item.get("query", "").strip()
        expected = item.get("expected_answer", "")
        category = item.get("category", "unknown")
        source   = item.get("source", "unknown")
        if not query:
            continue

        res      = ask_rag(query, tenant_id=TENANT_ID)
        answer   = res.get("answer", "")
        context  = res.get("context", "")
        scores   = evaluate_generation(query, context, answer)
        f_score  = scores.get("faithfulness", 0.0)
        r_score  = scores.get("relevance",    0.0)
        status   = "PASSED" if f_score >= 0.7 and r_score >= 0.7 else "FAILED"

        if status == "PASSED":
            passed += 1
        else:
            failed += 1

        print(f"[{i:02d}] {status}  F={f_score:.2f}  R={r_score:.2f}  [{source}|{category}]  {query[:70]}")
        records.append({
            "query": query, "expected": expected, "answer": answer,
            "faithfulness": f_score, "relevance": r_score,
            "status": status, "category": category, "source": source,
        })

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    total = len(records)

    # JSON
    json_path = os.path.join(RESULTS_DIR, f"baseline_eval_{ts}.json")
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)

    # Markdown
    md_path = os.path.join(RESULTS_DIR, f"baseline_eval_{ts}.md")
    avg_f = sum(r["faithfulness"] for r in records) / total
    avg_r = sum(r["relevance"]    for r in records) / total
    md = f"# Baseline Evaluation — {ts}\n\n"
    md += f"**Tenant:** {TENANT_ID} | **Total:** {total} | **Passed:** {passed} | **Failed:** {failed}\n\n"
    md += f"**Avg Faithfulness:** {avg_f:.3f} | **Avg Relevance:** {avg_r:.3f}\n\n"
    md += "| Source | Category | Query | F | R | Status |\n|---|---|---|---|---|---|\n"
    for r in records:
        md += f"| {r['source']} | {r['category']} | {r['query'][:55]}… | {r['faithfulness']:.2f} | {r['relevance']:.2f} | {r['status']} |\n"
    with open(md_path, 'w') as f:
        f.write(md)

    print(f"\n[SAVED] {json_path}")
    print(f"[SAVED] {md_path}")
    print(f"\nSummary: {passed}/{total} PASSED  |  Avg F={avg_f:.3f}  Avg R={avg_r:.3f}")


if __name__ == "__main__":
    run_baseline_eval()

"""
HyDE retrieval experiment script

This script compares baseline hybrid retrieval (`retrieve_hybrid`) against
HyDE-style pseudo-answer expansion retrieval. It uses existing components
from `src.core.retriever` and `src.core.pipeline`/`src.core.llm` where possible.

Flow:
 - Load evaluation dataset from `evaluation/dataset/evaluation_dataset.json`
 - For each query:
   - Run baseline hybrid retrieval (top_k)
   - Generate N pseudo-answers using `query_llm` (HyDE)
   - For each pseudo-answer, embed and run hybrid retrieval, then fuse results
   - Check whether `expected_answer` appears in combined retrieved context
 - Save per-query results and aggregate metrics to `experiments/results/`

Notes:
 - This script deliberately does not modify the stable pipeline. It only
   imports and reuses retriever functions and the shared embedder/LLM wrapper.
 - If no LLM provider is configured, HyDE will fall back to using the original
   query as a single pseudo-answer (graceful degradation).
"""

import os
import sys
import json
import time
import argparse
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

from src.core import retriever
from src.core.pipeline import embed_model
from src.core.llm import query_llm

RESULTS_DIR = "experiments/results"
DATASET_PATH = "evaluation/dataset/evaluation_dataset.json"
TOP_K = 20
FINAL_K = 5
HYDE_COUNT = 3


def print_safe(msg):
    """Print messages but avoid logging secrets (do not include env values)."""
    print(msg)


def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def baseline_hybrid(query, top_k=TOP_K):
    """Run the existing hybrid retriever and return list of (id, content, score)."""
    query_emb = embed_model.encode([query])[0].tolist()
    return retriever.retrieve_hybrid(query, query_emb, k=top_k)


def hyde_retrieval(query, hyde_count=HYDE_COUNT, top_k=TOP_K):
    """Generate hyde_count pseudo-answers, retrieve for each, and fuse results.

    Returns a fused list of (doc_id, content, fused_score).
    """
    # Prepare prompt to generate short plausible answers/hypotheses
    prompt = [
        {"role": "system", "content": "You are a concise answer generator. Produce short possible answers or hypotheses for the user's question. Separate multiple answers with ||"},
        {"role": "user", "content": f"Generate {hyde_count} plausible concise answers for: {query}"}
    ]

    hyde_text = None
    try:
        hyde_text = query_llm(prompt)
    except Exception as e:
        print(f"[WARN] HyDE LLM call failed: {e}")

    if not hyde_text or "[ERROR]" in hyde_text:
        # Fallback: use the original query as single pseudo-answer
        pseudo_answers = [query]
        print("[INFO] HyDE fallback: using original query as pseudo-answer.")
    else:
        # Expect responses separated by '||' or newlines
        if '||' in hyde_text:
            pseudo_answers = [p.strip() for p in hyde_text.split('||') if p.strip()][:hyde_count]
        else:
            # Split on newlines as fallback
            pseudo_answers = [p.strip() for p in hyde_text.splitlines() if p.strip()][:hyde_count]

    # Accumulate RRF-style scores across pseudo-queries
    combined = {}
    for pq_index, pa in enumerate(pseudo_answers):
        emb = embed_model.encode([pa])[0].tolist()
        results = retriever.retrieve_hybrid(pa, emb, k=top_k)
        for rank, (doc_id, content, score) in enumerate(results):
            if doc_id not in combined:
                combined[doc_id] = {"content": content, "score": 0.0}
            # Reciprocal rank fusion component
            combined[doc_id]["score"] += 1.0 / (10 + rank + 1)

    fused = sorted(combined.items(), key=lambda x: x[1]["score"], reverse=True)
    # return list of tuples (id, content, fused_score)
    return [(doc_id, data["content"], data["score"]) for doc_id, data in fused]


def evaluate_presence(retrieved_docs, expected_answer):
    """Check if expected_answer substring exists in combined retrieved text."""
    combined = "\n".join([doc for _, doc, _ in retrieved_docs[:FINAL_K]])
    if not expected_answer:
        return False
    return expected_answer.lower() in combined.lower()


def run_experiment():
    ensure_results_dir()

    # 1) Verify DB connection
    conn = retriever.get_connection()
    if not conn:
        print_safe("[ERROR] Unable to connect to the database. Check DB_HOST/PORT/credentials and ensure the DB is reachable.")
        return
    else:
        try:
            conn.close()
        except Exception:
            pass

    # 2) Verify rag_documents table exists and is populated
    if not retriever.check_table_exists():
        print_safe("[ERROR] Table 'rag_documents' does not exist or is empty. Run 'scripts/ingest_data.py' to populate the DB before running experiments.")
        return

    # 3) Load dataset and validate
    if not os.path.exists(DATASET_PATH):
        print_safe(f"[ERROR] Evaluation dataset not found at {DATASET_PATH}. Please create or copy it before running the experiment.")
        return

    dataset = load_dataset(DATASET_PATH)
    results = []
    stats = {"baseline_found": 0, "hyde_found": 0, "total": 0}

    if not dataset:
        print_safe("[ERROR] Evaluation dataset is empty. Add queries to the dataset before running the experiment.")
        return

    for entry in dataset:
        q = entry.get("query")
        expected = entry.get("expected_answer")
        stats["total"] += 1

        # Baseline hybrid
        base_res = baseline_hybrid(q, top_k=TOP_K)
        base_found = evaluate_presence(base_res, expected)
        if base_found:
            stats["baseline_found"] += 1

        # HyDE
        hyde_res = hyde_retrieval(q, hyde_count=HYDE_COUNT, top_k=TOP_K)
        hyde_found = evaluate_presence(hyde_res, expected)
        if hyde_found:
            stats["hyde_found"] += 1

        results.append({
            "query": q,
            "expected_answer": expected,
            "baseline_top_ids": [int(r[0]) for r in base_res[:FINAL_K]],
            "baseline_found": base_found,
            "hyde_top_ids": [int(r[0]) for r in hyde_res[:FINAL_K]],
            "hyde_found": hyde_found
        })

    # Aggregate metrics
    baseline_acc = stats["baseline_found"] / max(1, stats["total"])
    hyde_acc = stats["hyde_found"] / max(1, stats["total"])

    out = {
        "timestamp": time.strftime("%Y%m%d-%H%M%S"),
        "total_queries": stats["total"],
        "baseline_found": stats["baseline_found"],
        "hyde_found": stats["hyde_found"],
        "baseline_accuracy": baseline_acc,
        "hyde_accuracy": hyde_acc,
        "per_query": results
    }

    out_path = os.path.join(RESULTS_DIR, f"hyde_experiment_{out['timestamp']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print_safe(f"[DONE] Results saved to {out_path}")
    print_safe(f"Baseline accuracy: {baseline_acc:.3f}, HyDE accuracy: {hyde_acc:.3f}")


def validate_environment():
    """Validate required environment variables and connectivity for a dry-run or preflight.

    Returns a dict with status details.
    """
    status = {
        "llm_providers": {},
        "db_connectivity": False,
        "table_exists": False,
        "dataset_present": False,
        "dataset_count": 0
    }

    # Check LLM provider keys without printing them
    provs = ["GROQ_API_KEY", "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "GEMINI_API_KEY"]
    for p in provs:
        status["llm_providers"][p] = bool(os.getenv(p))

    # DB connectivity
    conn = retriever.get_connection()
    if conn:
        status["db_connectivity"] = True
        try:
            conn.close()
        except Exception:
            pass

    # Table existence
    status["table_exists"] = retriever.check_table_exists()

    # Dataset presence
    if os.path.exists(DATASET_PATH):
        try:
            ds = load_dataset(DATASET_PATH)
            status["dataset_present"] = True
            status["dataset_count"] = len(ds) if ds else 0
        except Exception:
            status["dataset_present"] = False

    return status


def main(argv=None):
    global HYDE_COUNT, TOP_K

    parser = argparse.ArgumentParser(description="HyDE retrieval experiment runner")
    parser.add_argument("--dry-run", action="store_true", help="Validate environment and dependencies without executing retrievals")
    parser.add_argument("--hyde-count", type=int, default=HYDE_COUNT, help="Number of pseudo-answers to generate per query")
    parser.add_argument("--top-k", type=int, default=TOP_K, help="top_k retrieval per pseudo-answer")
    args = parser.parse_args(argv)

    # Ensure GROQ preferred if available (query_llm already prefers GROQ, but we validate presence)
    groq_present = bool(os.getenv("GROQ_API_KEY"))
    if not groq_present:
        print_safe("[WARN] GROQ_API_KEY not found. The experiment will try other providers in order; set GROQ_API_KEY to prefer GROQ.")

    # Update globals per CLI
    HYDE_COUNT = args.hyde_count
    TOP_K = args.top_k

    status = validate_environment()

    # Dry-run: report and exit
    if args.dry_run:
        print_safe("[DRY-RUN] Environment validation results:")
        print_safe(f"  LLM providers present: {', '.join([k for k,v in status['llm_providers'].items() if v]) or 'none'}")
        print_safe(f"  DB connectivity: {'OK' if status['db_connectivity'] else 'FAILED'}")
        print_safe(f"  rag_documents table exists & populated: {'OK' if status['table_exists'] else 'MISSING/EMPTY'}")
        print_safe(f"  Dataset present: {'yes' if status['dataset_present'] else 'no'} (count={status['dataset_count']})")
        if not status['llm_providers'].get('GROQ_API_KEY') and not any(status['llm_providers'].values()):
            print_safe("[WARN] No LLM provider configured. HyDE will fall back to using the original query as pseudo-answer.")
        return

    # Run the experiment
    try:
        run_experiment()
    except Exception as e:
        print_safe(f"[ERROR] Experiment failed: {str(e)[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()

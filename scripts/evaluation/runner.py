import os
import sys
import datetime
import json
import mlflow

# Add project root to path

from src.core.pipeline import ask_rag
from src.evals.metrics import evaluate_generation
from src.core.database.connection import check_table_exists
from src.utils.config import settings

DATASET_PATH  = settings.EVALUATION_DATASET
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results')
TENANT_ID     = "metro_tenant"
MLFLOW_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'experiments', 'mlflow_runs'))

# Use file-based MLflow tracking — avoids readonly sqlite error on shared mlflow.db
os.makedirs(MLFLOW_DIR, exist_ok=True)
mlflow.set_tracking_uri(f"file://{MLFLOW_DIR}")


def load_queries_from_dataset(sources=None, exclude_sources=None):
    """Load queries from the golden dataset, optionally filtered by source."""
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if sources:
        data = [d for d in data if d.get("source") in sources]
    if exclude_sources:
        data = [d for d in data if d.get("source") not in exclude_sources]
    return [d["query"] for d in data if d.get("query")]

def run_experiment(exp_name, dataset_label, config, queries, tenant_id=TENANT_ID, entity_type=None, contract_standard=None, search_type="vector"):
    """
    Runs a batch of queries, logs to MLflow, saves log to experiments/ and experiments/results/.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_slug   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    exp_log_path = f"experiments/{exp_name}.md"
    results_path = os.path.join(RESULTS_DIR, f"{exp_name}_{ts_slug}.md")
    docs_path    = "docs/evaluation_results.md"
    
    exp_markdown = f"# Experiment: {exp_name}\n"
    exp_markdown += f"- **Date:** {timestamp}\n"
    exp_markdown += f"- **Dataset:** {dataset_label}\n"
    exp_markdown += f"- **Search Type:** {search_type}\n"
    exp_markdown += f"- **Tenant ID:** {tenant_id}\n"
    exp_markdown += f"- **Config:** {json.dumps(config)}\n\n"
    
    eval_results = []
    
    print(f"\n[INFO] Starting Experiment: {exp_name} | search={search_type} | tenant={tenant_id} | queries={len(queries)}")
    
    mlflow.set_experiment(exp_name)
    with mlflow.start_run():
        mlflow.log_params(config)
        mlflow.log_param("dataset", dataset_label)
        mlflow.log_param("search_type", search_type)
        mlflow.log_param("tenant_id", tenant_id)
        mlflow.log_param("num_queries", len(queries))
        
        for i, q in enumerate(queries):
            print(f"\nEvaluating Query: '{q}'")
            rag_result = ask_rag(
                query=q, 
                tenant_id=tenant_id, 
                entity_type=entity_type, 
                contract_standard=contract_standard,
                search_type=search_type
            )
            
            answer = rag_result.get("answer", "")
            context = rag_result.get("context", "")
            print(f"[DEBUG] Context length: {len(context)}")
            print(f"[DEBUG] Answer length: {len(answer)}")

            # Evaluate
            scores = evaluate_generation(q, context, answer)
            faithfulness = scores.get("faithfulness", 0.0)
            relevance = scores.get("relevance", 0.0)
            error = scores.get("error")
            
            # Determine status
            status = "PASSED" if not error and faithfulness >= 0.7 and relevance >= 0.7 else "FAILED"
            reason = "Scores >= 0.7" if status == "PASSED" else (f"Eval Error: {error}" if error else "Low faithfulness or relevance scores")
            fix = "N/A" if status == "PASSED" else "Check LLM availability or context retrieval/reranking"
                
            exp_markdown += f"## Query: {q}\n"
            exp_markdown += f"- **Result:** {status}\n"
            exp_markdown += f"- **Reason:** {reason}\n"
            exp_markdown += f"- **Faithfulness:** {faithfulness}\n"
            exp_markdown += f"- **Relevance:** {relevance}\n\n"
            
            eval_results.append({
                "query": q,
                "faithfulness": faithfulness,
                "relevance": relevance,
                "retrieved_chunks": rag_result.get("retrieved_chunks", []),
                "observations": f"{status} - {reason}"
            })
            
            mlflow.log_metric(f"faithfulness_{i}", faithfulness)
            mlflow.log_metric(f"relevance_{i}", relevance)
            print(f"  -> {status} (F: {faithfulness}, R: {relevance})")

    # Save experiment log (experiments/)
    os.makedirs("experiments", exist_ok=True)
    with open(exp_log_path, "w", encoding="utf-8") as f:
        f.write(exp_markdown)
    print(f"[SAVED] Experiment log → {exp_log_path}")
    
    # Save to experiments/results/
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        f.write(exp_markdown)
    print(f"[SAVED] Results → {results_path}")
        
    # Append to global docs
    os.makedirs("docs", exist_ok=True)
    mode = "a" if os.path.exists(docs_path) else "w"
    with open(docs_path, mode, encoding="utf-8") as f:
        if mode == "w": f.write("# Global Evaluation Results\n\n")
        f.write(f"## Experiment: {exp_name} ({timestamp})\n\n")
        for res in eval_results:
            f.write(f"### Query: {res['query']}\n")
            f.write(f"- **Faithfulness:** {res['faithfulness']}\n")
            f.write(f"- **Relevance:** {res['relevance']}\n")
            f.write(f"- **Chunks Retrieved:** {len(res.get('retrieved_chunks', []))}\n") # Add this line
            f.write(f"- **Observations:**\n  - {res['observations']}\n\n")

if __name__ == "__main__":
    if not check_table_exists():
        print("[ERROR] No data in DB. Run: python scripts/ingest_data.py first.")
        sys.exit(1)

    # Load queries from golden dataset (exclude adversarial for experiment runs)
    all_queries    = load_queries_from_dataset(exclude_sources=["adversarial"])
    breaking_query = load_queries_from_dataset(sources=["adversarial"])

    print(f"[INFO] Loaded {len(all_queries)} domain queries and {len(breaking_query)} adversarial queries.")

    # Exp 05: Full golden dataset — vector baseline (all sources)
    run_experiment(
        exp_name="exp_05_vector_golden_dataset",
        dataset_label="Golden Dataset (all sources, 30+ queries)",
        config={"top_k": 5, "final_k": 3},
        queries=all_queries,
        tenant_id=TENANT_ID,
        search_type="vector"
    )

    # Exp 06: Full golden dataset — hybrid search
    run_experiment(
        exp_name="exp_06_hybrid_golden_dataset",
        dataset_label="Golden Dataset (all sources, 30+ queries)",
        config={"top_k": 5, "final_k": 3},
        queries=all_queries,
        tenant_id=TENANT_ID,
        search_type="hybrid"
    )

    # Exp 07: Breaking — adversarial out-of-scope queries
    run_experiment(
        exp_name="exp_07_breaking_adversarial_oob",
        dataset_label="Adversarial Out-of-Scope (golden dataset)",
        config={"top_k": 5, "final_k": 3},
        queries=breaking_query,
        tenant_id=TENANT_ID,
        search_type="vector"
    )


import os
import sys
import datetime
import json
import mlflow

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import ask_rag
from src.evaluator import evaluate_generation

def run_experiment(exp_name, dataset, config, queries, tenant_id="default", entity_type=None, contract_standard=None):
    """
    Runs a batch of queries and generates an experiment log.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    exp_log_path = f"experiments/{exp_name}.md"
    results_path = "docs/evaluation_results.md"
    
    exp_markdown = f"# Experiment: {exp_name}\n"
    exp_markdown += f"- **Date:** {timestamp}\n"
    exp_markdown += f"- **Dataset:** {dataset}\n"
    exp_markdown += f"- **Config:** {json.dumps(config)}\n\n"
    
    eval_results = []
    
    print(f"\n[INFO] Starting Experiment: {exp_name}")
    
    mlflow.set_experiment(exp_name)
    with mlflow.start_run():
        mlflow.log_params(config)
        mlflow.log_param("dataset", dataset)
        
        for q in queries:
        print(f"\nEvaluating Query: '{q}'")
        rag_result = ask_rag(
            query=q, 
            tenant_id=tenant_id, 
            entity_type=entity_type, 
            contract_standard=contract_standard
        )
        
        answer = rag_result.get("answer", "")
        context = rag_result.get("context", "")
        
        # Evaluate
        scores = evaluate_generation(q, context, answer)
        faithfulness = scores.get("faithfulness", 0.0)
        relevance = scores.get("relevance", 0.0)
        error = scores.get("error")
        
        # Determine status
        if error:
            status = "FAILED"
            reason = f"Eval Error: {error}"
            fix = "Check LLM availability or context retrieval"
        elif faithfulness < 0.7 or relevance < 0.7:
            status = "FAILED"
            reason = "Low faithfulness or relevance scores"
            fix = "Improve retrieval metadata filtering or chunking"
        else:
            status = "PASSED"
            reason = "Scores >= 0.7"
            fix = "N/A"
            
        exp_markdown += f"## Query: {q}\n"
        exp_markdown += f"- **Result:** {status}\n"
        exp_markdown += f"- **Reason:** {reason}\n"
        exp_markdown += f"- **Fix:** {fix}\n"
        exp_markdown += f"- **Faithfulness:** {faithfulness}\n"
        exp_markdown += f"- **Relevance:** {relevance}\n\n"
        
        # Add to global evaluation results
        eval_results.append({
            "query": q,
            "faithfulness": faithfulness,
            "relevance": relevance,
            "observations": f"{status} - {reason}"
        })
        
        # Log to MLflow
        mlflow.log_metric(f"faithfulness_{q[:20]}", faithfulness)
        mlflow.log_metric(f"relevance_{q[:20]}", relevance)
        
        print(f"  -> {status} (F: {faithfulness}, R: {relevance})")

    # Save specific experiment log
    os.makedirs("experiments", exist_ok=True)
    with open(exp_log_path, "w", encoding="utf-8") as f:
        f.write(exp_markdown)
    print(f"\n[INFO] Saved experiment log to {exp_log_path}")
        
    # Append to global evaluation results
    os.makedirs("docs", exist_ok=True)
    mode = "a" if os.path.exists(results_path) else "w"
    with open(results_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# Global Evaluation Results\n\n")
            
        f.write(f"## Experiment: {exp_name} ({timestamp})\n\n")
        for res in eval_results:
            f.write(f"### Query: {res['query']}\n")
            f.write(f"- **Faithfulness:** {res['faithfulness']}\n")
            f.write(f"- **Relevance:** {res['relevance']}\n")
            f.write(f"- **Observations:**\n  - {res['observations']}\n\n")
            
    print(f"[INFO] Appended results to {results_path}")

if __name__ == "__main__":
    queries = [
        "What is the security deposit amount according to the contract?",
        "How is AI used in medicine?",
        "What happens in case of a breach of contract?"
    ]
    
    run_experiment(
        exp_name="exp_01_baseline_retrieval",
        dataset="GCC + Sample Docs",
        config={"top_k": 5, "final_k": 3},
        queries=queries,
        tenant_id="default",
        entity_type="contract",
        contract_standard="gcc"
    )

import os
import sys
import datetime
import json
import mlflow

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import ask_rag
from src.evaluator import evaluate_generation

def run_experiment(exp_name, dataset, config, queries, tenant_id="default", entity_type=None, contract_standard=None, search_type="vector"):
    """
    Runs a batch of queries and generates an experiment log.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    exp_log_path = f"experiments/{exp_name}.md"
    results_path = "docs/evaluation_results.md"
    
    exp_markdown = f"# Experiment: {exp_name}\n"
    exp_markdown += f"- **Date:** {timestamp}\n"
    exp_markdown += f"- **Dataset:** {dataset}\n"
    exp_markdown += f"- **Search Type:** {search_type}\n"
    exp_markdown += f"- **Config:** {json.dumps(config)}\n\n"
    
    eval_results = []
    
    print(f"\n[INFO] Starting Experiment: {exp_name} ({search_type})")
    
    mlflow.set_experiment(exp_name)
    with mlflow.start_run():
        mlflow.log_params(config)
        mlflow.log_param("dataset", dataset)
        mlflow.log_param("search_type", search_type)
        
        for q in queries:
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
                "observations": f"{status} - {reason}"
            })
            
            mlflow.log_metric(f"faithfulness_{q[:15]}", faithfulness)
            mlflow.log_metric(f"relevance_{q[:15]}", relevance)
            print(f"  -> {status} (F: {faithfulness}, R: {relevance})")

    # Save log
    os.makedirs("experiments", exist_ok=True)
    with open(exp_log_path, "w", encoding="utf-8") as f:
        f.write(exp_markdown)
        
    # Append to global docs
    os.makedirs("docs", exist_ok=True)
    mode = "a" if os.path.exists(results_path) else "w"
    with open(results_path, mode, encoding="utf-8") as f:
        if mode == "w": f.write("# Global Evaluation Results\n\n")
        f.write(f"## Experiment: {exp_name} ({timestamp})\n\n")
        for res in eval_results:
            f.write(f"### Query: {res['query']}\n")
            f.write(f"- **Faithfulness:** {res['faithfulness']}\n")
            f.write(f"- **Relevance:** {res['relevance']}\n")
            f.write(f"- **Observations:**\n  - {res['observations']}\n\n")

if __name__ == "__main__":
    queries = [
        "What is the security deposit amount according to the contract?",
        "Explain the procedure for breach of contract.",
        "What is the penalty for late performance bank guarantee?"
    ]
    
    # 1. Baseline Semantic
    run_experiment(
        exp_name="exp_02_semantic_baseline",
        dataset="GCC (Semantic Strategy)",
        config={"top_k": 5, "final_k": 3},
        queries=queries,
        tenant_id="semantic_strategy"
    )
    
    # 2. Hybrid Search Test
    run_experiment(
        exp_name="exp_03_hybrid_search",
        dataset="GCC (Semantic Strategy)",
        config={"top_k": 5, "final_k": 3},
        queries=queries,
        tenant_id="semantic_strategy",
        search_type="hybrid"
    )

    # 3. Breaking Experiment: Cross-Entity Confusion
    # Asking about 'DMRC' specifically while we only have 'GCC'
    breaking_queries = ["Does the DMRC agreement specify a different bank guarantee period?"]
    run_experiment(
        exp_name="exp_04_breaking_entity_confusion",
        dataset="GCC Only",
        config={"top_k": 5, "final_k": 3},
        queries=breaking_queries,
        tenant_id="semantic_strategy"
    )


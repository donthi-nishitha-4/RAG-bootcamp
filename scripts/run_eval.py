import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import ask_rag
from src.evals.metrics import evaluate_generation

def run_eval(queries):
    print(f"[INFO] Running evaluation on {len(queries)} queries...")
    for q in queries:
        print(f"\n--- Query: {q}")
        res = ask_rag(q)
        eval_res = evaluate_generation(q, res['context'], res['answer'])
        print(f"[ANSWER]: {res['answer'][:100]}...")
        print(f"[SCORES]: {eval_res}")

if __name__ == "__main__":
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
    test_queries = []
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            test_queries = [item['query'] for item in dataset if 'query' in item]
        print(f"[INFO] Loaded {len(test_queries)} queries from golden dataset.")
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        # Fallback to defaults
        test_queries = [
            "What is the security deposit amount?",
            "Explain the procedure for breach of contract."
        ]
        
    run_eval(test_queries)

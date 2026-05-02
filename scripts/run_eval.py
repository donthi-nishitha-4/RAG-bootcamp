import sys
import os

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
    test_queries = [
        "What is the security deposit amount?",
        "Explain the procedure for breach of contract."
    ]
    run_eval(test_queries)

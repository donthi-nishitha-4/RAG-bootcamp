import sys
import os
from src.core.pipeline import ask_rag
from src.evals.metrics import evaluate_generation

def run_legacy_eval():
    """
    Legacy entry point for Day 0 review.
    Correctly fixes DEF-01 by separating context and answer.
    """
    queries = [
        "What is the security deposit amount?",
        "Explain the procedure for breach of contract."
    ]
    
    print("--- Running Evaluation (DEF-01 Fixed) ---")
    for q in queries:
        # CORRECT: ask_rag returns both context and answer
        res = ask_rag(q, tenant_id="default_strategy")
        eval_res = evaluate_generation(q, res['context'], res['answer'])
        
        print(f"\nQuery: {q}")
        print(f"Answer: {res['answer'][:100]}...")
        print(f"Scores: {eval_res}")

if __name__ == "__main__":
    run_legacy_eval()

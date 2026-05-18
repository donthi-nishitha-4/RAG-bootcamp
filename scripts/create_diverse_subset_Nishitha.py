import os
import sys
import json
import argparse
from scripts.eval_ragas import run_ragas_evaluation

def run_diverse_eval(strategy="vector"):
    # Load full dataset
    data_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
    with open(data_path, 'r') as f:
        full_data = json.load(f)
    
    # Filter out adversarial
    clean_data = [d for d in full_data if d.get('category') != 'out_of_scope'] 
    
    # Diverse indices (5 queries)
    # GCC: 0 (Factual), 1 (Multi-hop)
    # DMRC: 8 (Analytical), 11 (Summary)
    # Kaggle: 20 (Analytical)
    diverse_indices = [0, 1, 8, 11, 20]
    diverse_data = [clean_data[i] for i in diverse_indices]
    
    # Save temporary diverse dataset
    temp_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'diverse_subset.json')
    with open(temp_path, 'w') as f:
        json.dump(diverse_data, f, indent=2)
    
    print(f"[INFO] Created diverse subset with {len(diverse_data)} entries.")
    
    # We need to temporarily point eval_ragas to this file or modify it
    # For simplicity, I'll just run a modified version of the logic here
    # Or better, I'll modify eval_ragas to accept a filename
    
if __name__ == "__main__":
    run_diverse_eval()

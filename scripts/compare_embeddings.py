import time
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import os

def compare_models():
    models = [
        "all-MiniLM-L6-v2",           # Current baseline
        "BAAI/bge-large-en-v1.5",     # High performance
        "nomic-ai/nomic-embed-text-v1.5" # Modern large context
    ]
    
    sample_texts = [
        "The security deposit shall be 5% of the contract value.",
        "Artificial intelligence is transforming the medical diagnosis field.",
        "A breach of contract occurs when one party fails to fulfill their obligations.",
        "The contractor must submit a performance bank guarantee within 30 days."
    ]
    
    print("--- Embedding Model Comparison ---")
    results = "# Embedding Model Comparison\n\n| Model | Dim | Latency (ms/doc) | Device |\n|---|---|---|---|\n"
    
    for model_name in models:
        print(f"\nLoading {model_name}...")
        start_load = time.time()
        try:
            # For nomic, we might need trust_remote_code=True
            if "nomic" in model_name:
                model = SentenceTransformer(model_name, trust_remote_code=True)
            else:
                model = SentenceTransformer(model_name)
            
            load_time = time.time() - start_load
            print(f"Loaded in {load_time:.2f}s")
            
            # Benchmark encoding
            start_enc = time.time()
            embeddings = model.encode(sample_texts)
            avg_latency = ((time.time() - start_enc) / len(sample_texts)) * 1000
            
            dim = embeddings.shape[1]
            device = "GPU" if torch.cuda.is_available() else "CPU"
            
            results += f"| {model_name} | {dim} | {avg_latency:.2f} | {device} |\n"
            print(f"Dim: {dim}, Latency: {avg_latency:.2f}ms")
            
        except Exception as e:
            print(f"Failed to load {model_name}: {e}")
            results += f"| {model_name} | N/A | FAILED | N/A |\n"

    # Save results to docs
    os.makedirs("docs", exist_ok=True)
    with open("docs/embedding_comparison.md", "w") as f:
        f.write(results)
    print(f"\n[SUCCESS] Results saved to docs/embedding_comparison.md")

if __name__ == "__main__":
    compare_models()

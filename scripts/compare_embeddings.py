import time
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import matplotlib.pyplot as plt
import umap

def compare_models():
    models = [
        "all-MiniLM-L6-v2",           
        "BAAI/bge-large-en-v1.5",     
        "nomic-ai/nomic-embed-text-v1.5"
    ]
    
    sample_texts = [
        "The security deposit shall be 5% of the contract value.",
        "Artificial intelligence is transforming medical diagnosis.",
        "A breach of contract occurs when one party fails to fulfill obligations.",
        "The contractor must submit a bank guarantee within 30 days.",
        "Deep learning models require massive amounts of data and compute.",
        "Contract termination procedures are outlined in Clause 60.",
        "Machine learning algorithms can predict maintenance needs.",
        "The consultant shall provide a progress report every month."
    ]
    
    print("--- Embedding Model Comparison & UMAP ---")
    results = "# Embedding Model Comparison\n\n| Model | Dim | Latency (ms/doc) | Device |\n|---|---|---|---|\n"
    
    all_embeddings = {}
    
    for model_name in models:
        print(f"\nLoading {model_name}...")
        try:
            if "nomic" in model_name:
                model = SentenceTransformer(model_name, trust_remote_code=True)
            else:
                model = SentenceTransformer(model_name)
            
            start_enc = time.time()
            embeddings = model.encode(sample_texts)
            avg_latency = ((time.time() - start_enc) / len(sample_texts)) * 1000
            
            dim = embeddings.shape[1]
            device = "GPU" if torch.cuda.is_available() else "CPU"
            results += f"| {model_name} | {dim} | {avg_latency:.2f} | {device} |\n"
            
            all_embeddings[model_name] = embeddings
            
        except Exception as e:
            print(f"Failed to load {model_name}: {e}")
            results += f"| {model_name} | N/A | FAILED | N/A |\n"

    # UMAP Visualization
    plt.figure(figsize=(10, 7))
    colors = ['red', 'blue', 'green']
    
    for i, (model_name, embeddings) in enumerate(all_embeddings.items()):
        reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, random_state=42)
        reduced = reducer.fit_transform(embeddings)
        plt.scatter(reduced[:, 0], reduced[:, 1], c=colors[i], label=model_name, alpha=0.6)
        for j, text in enumerate(sample_texts):
            plt.annotate(f"{j}", (reduced[j, 0], reduced[j, 1]), fontsize=8)

    plt.title("UMAP Projection of Different Embedding Models")
    plt.legend()
    os.makedirs("docs/images", exist_ok=True)
    plt.savefig("docs/images/umap_comparison.png")
    print("\n[SUCCESS] UMAP plot saved to docs/images/umap_comparison.png")

    results += "\n![UMAP Comparison](images/umap_comparison.png)\n"
    
    os.makedirs("docs", exist_ok=True)
    with open("docs/embedding_comparison.md", "w") as f:
        f.write(results)
    print(f"[SUCCESS] Results saved to docs/embedding_comparison.md")

if __name__ == "__main__":
    compare_models()

import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retriever import load_documents, init_pgvector
import numpy as np

if __name__ == "__main__":
    init_pgvector()
    docs = ["Test doc"]
    embs = [np.zeros(384).tolist()]
    load_documents(docs, embs, tenant_id="test_tenant_123")
    print("Done")

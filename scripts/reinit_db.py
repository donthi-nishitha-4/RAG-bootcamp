import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.retriever import init_pgvector

if __name__ == "__main__":
    if init_pgvector():
        print("[SUCCESS] DB re-initialized with pg_trgm support.")
    else:
        print("[ERROR] DB init failed.")

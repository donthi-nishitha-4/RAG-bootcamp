import os
import sys

# Add project root to path

from src.core.database.connection import init_pgvector

if __name__ == "__main__":
    if init_pgvector():
        print("[SUCCESS] DB re-initialized with pg_trgm support.")
    else:
        print("[ERROR] DB init failed.")

# src/core/database/connection.py
import psycopg2
import os
import sys
import numpy as np
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from src.utils.config import settings

# --- DB CONNECTION CONFIG ---
# Use centralized settings
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
# Note: Add DB_NAME, DB_USER, DB_PASS to your config.py if not there, 
# for now we'll keep the env fallback here
DB_NAME = os.getenv("DB_NAME", "rag_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

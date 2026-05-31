# src/utils/config.py
from pathlib import Path
from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DMRC_DATASET: Path = DATA_DIR / "dmrc" / "dmrc_Synthetic_Dataset_Nishitha.json"
    RESULTS_DIR: Path = PROJECT_ROOT / "experiments" / "results"
    AUDIT_LOG_FILE: Path = RESULTS_DIR / "audit_events_ledger_Nishitha.json"
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    
    # ==================== LLM PROVIDERS ====================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # ==================== SECURITY ====================
    MAX_LATENCY_MS: int = 5000

    class Config:
        case_sensitive = True

settings = Settings()
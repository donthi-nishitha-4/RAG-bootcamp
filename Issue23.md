## When to Use This Document

**Use this AFTER:**
- ✅ All 5 data integrity fixes are merged
- ✅ All 6 security hardening layers are in place
- ✅ All tests pass (57 tests)
- ✅ Docker builds and API runs locally

**Then follow this step-by-step** to refactor the directory structure from bootcamp (contributor names everywhere) to production (modular, scalable).

---

## Part 1: Pre-Migration Checklist

### Before You Start

**Verify these are done:**
```bash
# 1. All tests pass
pytest tests/ -v
# Output: ✅ 57 passed

# 2. API runs
uvicorn src.api.main:app --reload
# Output: ✅ Application startup complete

# 3. Docker works
docker-compose up
# Output: ✅ API service up on 8000

# 4. No hardcoded paths remain (from previous fixes)
grep -r '"data/' src/ || echo "✅ No hardcoded paths in src/"
grep -r '"experiments/' src/ || echo "✅ No hardcoded paths in src/"

# 5. Current structure is documented
git log --oneline | head -5
# Should show previous fixes merged
```

If anything fails, **don't proceed**. Go back and fix it.

---

### Backup Everything

```bash
# Create a backup branch BEFORE starting migration
git checkout -b migration/production-structure
git commit -m "Pre-migration backup - all fixes in place"

# If migration goes wrong, you can always revert
git reset --hard migration/production-structure
```

---

## Part 2: Step-by-Step Migration

### Phase 1: Create New Directory Structure (30 mins)

**Goal:** Create the new structure WITHOUT moving files yet.

#### Step 1.1: Create Core Directories

```bash
# Create new src/ subdirectories
mkdir -p src/core/database
mkdir -p src/core/security
mkdir -p src/api/routes
mkdir -p src/api/middleware
mkdir -p src/agents
mkdir -p src/utils

# Create test directories
mkdir -p tests/unit
mkdir -p tests/integration

# Create scripts directories
mkdir -p scripts/ingest
mkdir -p scripts/evaluation
mkdir -p scripts/dev
mkdir -p scripts/migration

# Create research directories
mkdir -p research/shared
mkdir -p research/contributor1
mkdir -p research/contributor2

# Create docs directories
mkdir -p docs

# Verify structure
tree -d -L 3 src/
# Should show all new directories
```

#### Step 1.2: Create `__init__.py` Files

```bash
# Create empty __init__.py files (Python package markers)
touch src/__init__.py
touch src/core/__init__.py
touch src/core/database/__init__.py
touch src/core/security/__init__.py
touch src/api/__init__.py
touch src/api/routes/__init__.py
touch src/api/middleware/__init__.py
touch src/agents/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch scripts/__init__.py
touch scripts/ingest/__init__.py
touch scripts/evaluation/__init__.py
touch scripts/dev/__init__.py
touch research/__init__.py
touch research/shared/__init__.py
touch research/contributor1/__init__.py
touch research/contributor2/__init__.py

# Verify all created
find src tests scripts research -name '__init__.py' | wc -l
# Should output: 18+
```

✅ **Checkpoint:** New directory structure is in place. Old files still exist (we'll move them next).

---

### Phase 2: Create Configuration System (20 mins)

**Goal:** Centralize all paths and settings in one file BEFORE moving code.

#### Step 2.1: Create `src/utils/config.py`

```python
# src/utils/config.py

"""
Centralized configuration for the RAG application.
This is the single source of truth for all paths and settings.
No hardcoded paths should exist anywhere else in the codebase.
"""

from pathlib import Path
from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Usage:
        from src.utils.config import settings
        path = settings.DMRC_DATASET
        db_host = settings.DB_HOST
    """
    
    # ==================== PATHS ====================
    # All relative paths computed from PROJECT_ROOT
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    
    # Data directories
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DMRC_DIR: Path = DATA_DIR / "dmrc"
    CORRESPONDENCE_DIR: Path = DATA_DIR / "correspondence"
    
    # Dataset files
    DMRC_DATASET: Path = DMRC_DIR / "dmrc_Synthetic_Dataset_Nishitha.json"
    TAXONOMY_XLSX: Path = DATA_DIR / "Metro_Rail_Consolidated_Systems_Taxonomy.xlsx"
    
    # Evaluation
    EVALUATION_DATASET: Path = PROJECT_ROOT / "evaluation" / "dataset" / "evaluation_dataset.json"
    
    # Results and logs
    RESULTS_DIR: Path = PROJECT_ROOT / "experiments" / "results"
    AUDIT_LOG_FILE: Path = RESULTS_DIR / "audit_events_ledger.json"
    
    # ==================== DATABASE ====================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "rag_db")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct full PostgreSQL connection string"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ==================== LLM PROVIDERS ====================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Default LLM model
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", 0.1))
    
    # ==================== RETRIEVAL SETTINGS ====================
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 128))
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", 5))
    RERANKER_TOP_K: int = int(os.getenv("RERANKER_TOP_K", 3))
    
    # ==================== SECURITY ====================
    API_KEY_REQUIRED: bool = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 10))
    RATE_LIMIT_PERIOD_SECONDS: int = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", 60))
    
    # PII redaction
    PII_REDACTION_ENABLED: bool = os.getenv("PII_REDACTION_ENABLED", "true").lower() == "true"
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or plain
    
    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __post_init__(self):
        """Validate paths exist"""
        # Data directories should exist
        assert self.DATA_DIR.exists(), f"DATA_DIR does not exist: {self.DATA_DIR}"
        assert self.CORRESPONDENCE_DIR.exists(), f"CORRESPONDENCE_DIR does not exist: {self.CORRESPONDENCE_DIR}"
        
        # Results directory should exist (create if not)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Singleton instance - use throughout the app
settings = Settings()

# Export for convenience
__all__ = ["settings", "Settings"]
```

#### Step 2.2: Create `.env.example`

```bash
# .env.example
# Copy to .env and fill in your actual values

# ==================== DATABASE ====================
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=rag_db

# ==================== LLM PROVIDERS ====================
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...
GEMINI_API_KEY=...

# Default LLM
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1

# ==================== RETRIEVAL ====================
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=128
RETRIEVAL_TOP_K=5
RERANKER_TOP_K=3

# ==================== SECURITY ====================
API_KEY_REQUIRED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD_SECONDS=60
PII_REDACTION_ENABLED=true

# ==================== LOGGING ====================
LOG_LEVEL=INFO
LOG_FORMAT=json

# ==================== ENVIRONMENT ====================
ENVIRONMENT=development
DEBUG=false
```

#### Step 2.3: Test Configuration

```bash
# Test that config loads correctly
python -c "
from src.utils.config import settings
print('✅ Config loaded successfully')
print(f'PROJECT_ROOT: {settings.PROJECT_ROOT}')
print(f'DB_HOST: {settings.DB_HOST}')
print(f'DMRC_DATASET: {settings.DMRC_DATASET}')
print(f'RESULTS_DIR: {settings.RESULTS_DIR}')
"
# Should output: ✅ Config loaded successfully + paths
```

✅ **Checkpoint:** Configuration system is in place and working.

---

### Phase 3: Create Public API Exports (15 mins)

**Goal:** Create `__init__.py` files that export public APIs so imports work correctly.

#### Step 3.1: Create `src/core/__init__.py`

```python
# src/core/__init__.py

"""
RAG core modules - the heart of the application.
All imports are centralized here for easy discovery.
"""

# Database
from src.core.database.connection import get_db, get_connection

# Retrieval
from src.core.retrieval import (
    retrieve_vectors,
    retrieve_bm25,
    retrieve_hybrid,
)

# Reranking
from src.core.reranking import rerank_results

# LLM
from src.core.llm.provider import query_llm

# Security
from src.core.security.pii_redaction import PIIRedactor
from src.core.security.prompt_injection import PromptInjectionFilter
from src.core.security.oos_filter import DomainOOSFilter
from src.core.security.audit import AuditLogger

# Evaluation
from src.core.evaluation import evaluate_ragas, compute_metrics

# Export public API
__all__ = [
    "get_db",
    "get_connection",
    "retrieve_vectors",
    "retrieve_bm25",
    "retrieve_hybrid",
    "rerank_results",
    "query_llm",
    "PIIRedactor",
    "PromptInjectionFilter",
    "DomainOOSFilter",
    "AuditLogger",
    "evaluate_ragas",
    "compute_metrics",
]
```

#### Step 3.2: Create `src/api/__init__.py`

```python
# src/api/__init__.py

"""
FastAPI application and routes.
"""

from src.api.main import app

__all__ = ["app"]
```

#### Step 3.3: Create `src/agents/__init__.py`

```python
# src/agents/__init__.py

"""
Agent orchestration - LangGraph and routing.
"""

from src.agents.langgraph_agent import run_agentic_query
from src.agents.query_router import route_query

__all__ = ["run_agentic_query", "route_query"]
```

✅ **Checkpoint:** Public APIs are exported correctly.

---

### Phase 4: Move and Refactor Code Files (90 mins)

**This is the longest phase. Take your time.**

#### Step 4.1: Move API Files

```bash
# Move API file
# OLD: src/api_Nishitha.py → NEW: src/api/main.py
mv src/api_Nishitha.py src/api/main.py

# Update imports in src/api/main.py
# Find and replace all:
# OLD: from src.core.agent_Nishitha import run_agentic_query
# NEW: from src.agents.langgraph_agent import run_agentic_query

# OLD: from src.core.hardening_Nishitha import check_out_of_scope
# NEW: from src.core.security.prompt_injection import is_injection_attempt

# OLD: from src.core.hardening_Nishitha import generate_citations
# NEW: from src.core.security.audit import generate_citations

# Test API
python -c "from src.api.main import app; print('✅ API imports work')"
```

#### Step 4.2: Move Agent Files

```bash
# Move agent files
# OLD: src/core/agent_Nishitha.py → NEW: src/agents/langgraph_agent.py
mv src/core/agent_Nishitha.py src/agents/langgraph_agent.py

# OLD: src/core/query_router_Nishitha.py → NEW: src/agents/query_router.py
mv src/core/query_router_Nishitha.py src/agents/query_router.py

# Update imports in src/agents/langgraph_agent.py
# OLD: from src.core.retriever import retrieve
# NEW: from src.core.retrieval import retrieve

# OLD: from src.core.llm import query_llm
# NEW: from src.core.llm.provider import query_llm

# OLD: hardcoded path "data/dmrc/dmrc_Synthetic_Dataset_Nishitha.json"
# NEW: from src.utils.config import settings
#      path = settings.DMRC_DATASET

# Test agent
python -c "from src.agents.langgraph_agent import run_agentic_query; print('✅ Agent imports work')"
```

#### Step 4.3: Move Database Files

```bash
# Move database module
# OLD: src/core/retriever.py → NEW: src/core/database/connection.py
mv src/core/retriever.py src/core/database/connection.py

# Update imports in src/core/database/connection.py
# OLD: hardcoded "DB_HOST = os.getenv('DB_HOST', 'localhost')"
# NEW: from src.utils.config import settings
#      db_host = settings.DB_HOST

# Test database
python -c "from src.core.database.connection import get_db; print('✅ Database imports work')"
```

#### Step 4.4: Move Security Files

```bash
# Create security module
# OLD: src/core/hardening_Nishitha.py → NEW: src/core/security/* (split into multiple)

# Move (don't delete yet, we'll split it)
cp src/core/hardening_Nishitha.py src/core/security/hardening_backup.py

# Create new security files from hardening_Nishitha.py
# src/core/security/pii_redaction.py (PII redaction logic)
# src/core/security/prompt_injection.py (Prompt injection detection)
# src/core/security/oos_filter.py (OOS filter with embeddings)
# src/core/security/audit.py (Audit logging)
# src/core/security/rls.py (Row-level security setup)

# Update imports in each security file
# OLD: from src.core.retriever import get_connection
# NEW: from src.core.database.connection import get_connection

# OLD: hardcoded "experiments/results/audit_events_ledger_Nishitha.json"
# NEW: from src.utils.config import settings
#      path = settings.AUDIT_LOG_FILE

# Test security
python -c "from src.core.security.pii_redaction import PIIRedactor; print('✅ Security imports work')"
```

#### Step 4.5: Move Test Files

```bash
# Move test files from scripts/ to tests/
# OLD: scripts/test_api_Nishitha.py → NEW: tests/integration/test_api.py
mv scripts/test_api_Nishitha.py tests/integration/test_api.py

# OLD: scripts/test_agent_Nishitha.py → NEW: tests/integration/test_agent.py
mv scripts/test_agent_Nishitha.py tests/integration/test_agent.py

# OLD: scripts/test_hardening_Nishitha.py → NEW: tests/unit/test_security.py
mv scripts/test_hardening_Nishitha.py tests/unit/test_security.py

# OLD: scripts/test_query_router_Nishitha.py → NEW: tests/unit/test_routing.py
mv scripts/test_query_router_Nishitha.py tests/unit/test_routing.py

# Update imports in all test files
# OLD: from src.api_Nishitha import app
# NEW: from src.api.main import app

# OLD: from src.core.agent_Nishitha import run_agentic_query
# NEW: from src.agents.langgraph_agent import run_agentic_query

# OLD: from src.core.hardening_Nishitha import check_security
# NEW: from src.core.security.prompt_injection import check_security

# Test tests
pytest tests/ -v
# Should pass: ✅ 57 passed
```

#### Step 4.6: Move Script Files

```bash
# Organize scripts by purpose
# OLD: scripts/ (mixed)
# NEW: scripts/ingest/, scripts/evaluation/, scripts/dev/

# Data ingestion scripts
mv scripts/ingest_data.py scripts/ingest/from_pdf.py
mv scripts/ingest_taxonomy.py scripts/ingest/from_xlsx.py
mv scripts/correspondence_chunker_Nishitha.py scripts/ingest/from_txt.py

# Evaluation scripts
mv scripts/run_eval.py scripts/evaluation/benchmark.py
mv scripts/eval_ragas.py scripts/evaluation/ragas.py
mv scripts/run_experiments.py scripts/evaluation/runner.py

# Development scripts
mv scripts/demo_graph_rag.py scripts/dev/demo_graph_rag.py
mv scripts/compare_embeddings_Nishitha.py scripts/dev/embedding_benchmark.py

# Update imports in all scripts
# OLD: from src.core.retriever import get_connection
# NEW: from src.core.database.connection import get_connection

# OLD: hardcoded path "evaluation/dataset/evaluation_dataset.json"
# NEW: from src.utils.config import settings
#      path = settings.EVALUATION_DATASET

# Test scripts
python scripts/ingest/from_pdf.py --help  # Should work
python scripts/evaluation/benchmark.py --help  # Should work
```

✅ **Checkpoint:** All code files are moved and imports updated.

---

### Phase 5: Delete Old Files (10 mins)

**Only delete after Phase 4 is verified working.**

```bash
# Delete old API file
rm src/api_Nishitha.py || echo "Already deleted"

# Delete old agent files
rm src/core/agent_Nishitha.py || echo "Already deleted"
rm src/core/query_router_Nishitha.py || echo "Already deleted"

# Delete old hardening file
rm src/core/hardening_Nishitha.py || echo "Already deleted"

# Delete old retriever file
rm src/core/retriever.py || echo "Already deleted"

# Delete old test scripts from scripts/
rm scripts/test_*.py || echo "Already deleted"

# Delete old hardening backup
rm src/core/security/hardening_backup.py || echo "Already deleted"

# Delete any old chunker files with contributor names
rm src/chunkers/*_BALU.py || echo "Already deleted"
rm src/chunkers/*_NISHITHA.py || echo "Already deleted"

# Verify no old files remain
find . -name "*_Nishitha.py" -o -name "*_BALU.py" | wc -l
# Should output: 0
```

✅ **Checkpoint:** Old files are deleted. No duplicates remain.

---

### Phase 6: Run Full Test Suite (15 mins)

**Critical: Verify everything still works.**

```bash
# 1. Run all tests
pytest tests/ -v --tb=short
# Output: ✅ 57 passed in X.XXs

# 2. Check test coverage
pytest tests/ --cov=src --cov-report=term-missing
# Output: Coverage 87%+ is good

# 3. Check for import errors
python -m py_compile src/**/*.py
# Output: No errors

# 4. Test API startup
uvicorn src.api.main:app --reload &
sleep 3
curl http://localhost:8000/health
# Output: 200 OK
kill %1

# 5. Test Docker
docker-compose up -d
sleep 5
curl http://localhost:8000/health
# Output: 200 OK
docker-compose down

# 6. Check no hardcoded paths remain
grep -r '"data/' src/ || echo "✅ No hardcoded paths"
grep -r '"experiments/' src/ || echo "✅ No hardcoded paths"
grep -r '"evaluation/' src/ || echo "✅ No hardcoded paths"
```

✅ **Checkpoint:** All tests pass. API works. Docker works. No hardcoded paths.

---

### Phase 7: Update Documentation (15 mins)

```bash
# Create migration guide
cat > docs/MIGRATION_GUIDE.md << 'EOF'
# Migration Guide: Bootcamp → Production

## What Changed

### Old Import Paths → New Import Paths

| Old | New |
|-----|-----|
| `from src.api_Nishitha import app` | `from src.api.main import app` |
| `from src.core.agent_Nishitha import run_agentic_query` | `from src.agents.langgraph_agent import run_agentic_query` |
| `from src.core.query_router_Nishitha import route_query` | `from src.agents.query_router import route_query` |
| `from src.core.retriever import get_connection` | `from src.core.database.connection import get_connection` |
| `from src.core.hardening_Nishitha import redact_pii` | `from src.core.security.pii_redaction import PIIRedactor` |
| Hardcoded `"data/dmrc/..."` | `from src.utils.config import settings; settings.DMRC_DATASET` |

## How to Use New Imports

```python
# ✅ Good: Use from new location
from src.agents.langgraph_agent import run_agentic_query
from src.core.database.connection import get_db
from src.utils.config import settings

# ✅ Good: Use public API exports
from src.core import query_llm, retrieve_vectors
from src.api import app

# ❌ Bad: Don't use old paths
# from src.api_Nishitha import app  # OLD
# from src.core.hardening_Nishitha import redact_pii  # OLD
```

## Configuration

All paths and settings are now centralized in `src/utils/config.py`.

```python
from src.utils.config import settings

# ✅ Use settings for all paths
path = settings.DMRC_DATASET
db_url = settings.DATABASE_URL
log_level = settings.LOG_LEVEL

# ❌ Don't hardcode paths
# path = "data/dmrc/dmrc_Synthetic_Dataset_Nishitha.json"  # OLD
```

## Running the System

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API
uvicorn src.api.main:app --reload

# Run tests
pytest tests/ -v

# Run ingestion
python scripts/ingest/from_pdf.py
```

### Docker Deployment
```bash
docker-compose up
curl http://localhost:8000/health
```

## Contributing

When adding new code:
1. Add files to the appropriate module (`src/core/`, `src/agents/`, `src/api/`, etc.)
2. Update the module's `__init__.py` to export public APIs
3. Use `from src.utils.config import settings` for all paths
4. Add tests in `tests/unit/` or `tests/integration/`
5. Update imports in related files

See `docs/CONTRIBUTING.md` for more details.
EOF

# Create architecture doc
cat > docs/ARCHITECTURE.md << 'EOF'
# Architecture: Production-Ready RAG System

## Directory Structure

```
src/
├── api/              # FastAPI application
├── agents/           # LangGraph and routing
├── core/
│   ├── database/     # PostgreSQL connection
│   ├── retrieval/    # Vector/BM25/hybrid
│   ├── security/     # PII, audit, RLS
│   ├── llm/          # LLM providers
│   └── evaluation/   # Metrics, testing
└── utils/            # Config, logging, types
```

## Import Rules

1. **Core modules** export public APIs via `__init__.py`
   ```python
   # Use public API
   from src.core import query_llm, retrieve_vectors
   ```

2. **Configuration** comes from `src/utils/config.py`
   ```python
   from src.utils.config import settings
   ```

3. **No circular imports**
   - `src/core/` imports only from `src/utils/`
   - `src/api/` imports from `src/core/` and `src/agents/`
   - `src/agents/` imports from `src/core/`

## Adding New Features

### New LLM Provider
1. Create `src/core/llm/new_provider.py`
2. Implement provider interface
3. Update `src/core/llm/__init__.py`

### New Retrieval Strategy
1. Create `src/core/retrieval/new_strategy.py`
2. Implement retrieval interface
3. Update `src/core/retrieval/__init__.py`

### New Security Layer
1. Create `src/core/security/new_check.py`
2. Implement security interface
3. Update `src/core/security/__init__.py`

## Deployment

All paths are relative to `PROJECT_ROOT`, so structure works:
- Local development (Unix/Windows)
- Docker containers
- Cloud environments (AWS/GCP/Azure)

No `cd` hacks needed. No hardcoded paths.
EOF

# Verify docs created
ls -la docs/MIGRATION_GUIDE.md docs/ARCHITECTURE.md
# Should output: both files
```

✅ **Checkpoint:** Documentation is updated.

---

### Phase 8: Final Verification & Commit (20 mins)

```bash
# 1. Final sanity checks
echo "=== Running Final Checks ==="

# Check structure
echo "✅ Checking structure..."
test -d src/core/database && echo "  ✅ src/core/database exists"
test -d src/core/security && echo "  ✅ src/core/security exists"
test -d src/api && echo "  ✅ src/api exists"
test -d src/agents && echo "  ✅ src/agents exists"
test -d tests/unit && echo "  ✅ tests/unit exists"
test -d tests/integration && echo "  ✅ tests/integration exists"
test -d scripts/ingest && echo "  ✅ scripts/ingest exists"
test -d scripts/evaluation && echo "  ✅ scripts/evaluation exists"

# Check config
echo "✅ Checking config..."
python -c "from src.utils.config import settings; print('  ✅ Config loads')"

# Check imports
echo "✅ Checking imports..."
python -c "from src.api.main import app; print('  ✅ API imports')"
python -c "from src.agents.langgraph_agent import run_agentic_query; print('  ✅ Agent imports')"
python -c "from src.core import query_llm; print('  ✅ Core imports')"

# Run tests
echo "✅ Running tests..."
pytest tests/ -q --tb=no
# Should output: 57 passed in X.XXs

# Check for old files
echo "✅ Checking for old files..."
OLD_FILES=$(find . -name "*_Nishitha.py" -o -name "*_BALU.py" | wc -l)
if [ "$OLD_FILES" -eq "0" ]; then
  echo "  ✅ No old files found"
else
  echo "  ❌ WARNING: Found $OLD_FILES old files"
fi

# 2. Commit migration
echo "=== Committing Migration ==="
git add -A
git commit -m "refactor: Migrate from bootcamp to production structure

- Rename API file: src/api_Nishitha.py → src/api/main.py
- Rename agent files: src/core/agent_Nishitha.py → src/agents/langgraph_agent.py
- Move database: src/core/retriever.py → src/core/database/connection.py
- Split security: src/core/hardening_Nishitha.py → src/core/security/*
- Move tests: scripts/test_*.py → tests/unit/ and tests/integration/
- Organize scripts: scripts/* → scripts/ingest/, scripts/evaluation/, scripts/dev/
- Centralize config: src/utils/config.py (single source of truth)
- Remove contributor names from filenames
- Update all imports (see MIGRATION_GUIDE.md)
- All 57 tests pass
- Docker builds and runs

This is the final architectural refactoring.
Next step: Production deployment."

# 3. Create clean branch for review
git log --oneline -1
# Should show your commit
```

✅ **Checkpoint:** Migration is complete and committed.

---

## Part 3: Common Mistakes & How to Avoid Them

### Mistake 1: Forgetting to Update Imports Everywhere

**Problem:**
```python
# You moved the file:
# OLD: src/core/agent_Nishitha.py
# NEW: src/agents/langgraph_agent.py

# But forgot to update imports in main.py
from src.core.agent_Nishitha import run_agentic_query  # ❌ BROKEN
```

**How to Avoid:**
```bash
# Find all old import patterns
grep -r "from src.core.agent_Nishitha" src/
grep -r "from src.core.hardening_Nishitha" src/
grep -r "from src.core.query_router_Nishitha" src/
grep -r "from src.core.retriever import" src/

# Replace them systematically
# Use find-replace in your editor
# OLD → NEW
# from src.core.agent_Nishitha → from src.agents.langgraph_agent
# from src.core.query_router_Nishitha → from src.agents.query_router
# from src.core.hardening_Nishitha → from src.core.security.*
# from src.core.retriever → from src.core.database.connection
```

---

### Mistake 2: Hardcoded Paths Still Exist

**Problem:**
```python
# You updated some files but missed others
path = "data/dmrc/dmrc_Synthetic_Dataset_Nishitha.json"  # ❌ BREAKS in Docker
```

**How to Avoid:**
```bash
# Find ALL hardcoded paths
grep -r '"data/' src/
grep -r '"experiments/' src/
grep -r '"evaluation/' src/

# Replace ALL with config
# OLD: path = "data/dmrc/..."
# NEW: from src.utils.config import settings
#      path = settings.DMRC_DATASET
```

---

### Mistake 3: Circular Imports

**Problem:**
```python
# src/core/security/pii_redaction.py
from src.api.main import app  # ❌ CIRCULAR

# src/api/main.py
from src.core.security.pii_redaction import PIIRedactor  # ❌ CIRCULAR
```

**How to Avoid:**
```python
# ✅ CORRECT dependency direction:
# src/api/ imports from src/core/
# src/core/ NEVER imports from src/api/

# If you need shared logic, put it in src/utils/ or src/core/
from src.utils.config import settings  # ✅ SAFE
from src.core.security.pii_redaction import PIIRedactor  # ✅ SAFE
```

**Check for circular imports:**
```bash
python -m py_compile src/**/*.py
# If no errors, you're good
```

---

### Mistake 4: Tests Import Old Paths

**Problem:**
```python
# tests/integration/test_api.py
from src.api_Nishitha import app  # ❌ OLD PATH

# Should be:
from src.api.main import app  # ✅ NEW PATH
```

**How to Avoid:**
```bash
# Search test files for old imports
grep -r "from src.api_Nishitha" tests/
grep -r "from src.core.agent_Nishitha" tests/
grep -r "from src.core.hardening_Nishitha" tests/

# Replace all old imports
pytest tests/ -v
# All should pass
```

---

### Mistake 5: Forgot `__init__.py` Files

**Problem:**
```bash
# You created src/core/security/ but forgot __init__.py
mkdir -p src/core/security
# (no __init__.py)

# Now imports break
from src.core.security.pii_redaction import PIIRedactor  # ❌ ModuleNotFoundError
```

**How to Avoid:**
```bash
# Create __init__.py in EVERY package directory
touch src/core/security/__init__.py

# Verify all exist
find src -type d -exec test -f {}/__init__.py \; -print
# Should list all directories
```

---

### Mistake 6: Docker Still Points to Old Paths

**Problem:**
```yaml
# docker-compose.yml
command: uvicorn src.api_Nishitha:app --host 0.0.0.0 --port 8000
# ❌ WRONG: app has moved to src/api/main.py
```

**How to Fix:**
```yaml
# docker-compose.yml
command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
# ✅ CORRECT: points to new location
```

---

## Part 4: Token-Saving Tips for LLM Assistance

**If you get stuck during migration and need Claude/ChatGPT help, use these prompts to save tokens:**

### Prompt Template 1: Import Fixing

```
I'm migrating a Python project from old paths to new paths.

OLD STRUCTURE:
src/
├── api_Nishitha.py
├── core/agent_Nishitha.py
├── core/hardening_Nishitha.py
└── core/retriever.py

NEW STRUCTURE:
src/
├── api/main.py
├── agents/langgraph_agent.py
├── core/security/
└── core/database/connection.py

Find all imports matching:
- from src.api_Nishitha
- from src.core.agent_Nishitha
- from src.core.hardening_Nishitha
- from src.core.retriever

And show me the replacements.
```

**Why it saves tokens:**
- You provide structure once, not repeatedly
- LLM understands pattern and applies it everywhere
- Avoids back-and-forth clarifications

---

### Prompt Template 2: Configuration Extraction

```
Here's a file with hardcoded paths:

[PASTE FILE CONTENT]

Extract ALL hardcoded paths and show me replacements using:
from src.utils.config import settings

List in this format:
OLD: "path/to/something"
NEW: settings.SOMETHING_VAR
```

**Why it saves tokens:**
- Focused on one task
- Clear input/output format
- LLM gives you exact replacements

---

### Prompt Template 3: Circular Import Detection

```
Check this import structure for circular dependencies:

src/api/main.py imports from:
- src.core.security
- src.agents.langgraph_agent

src/core/security/__init__.py imports from:
- src.utils.config

src/agents/langgraph_agent.py imports from:
- src.core.database.connection
- src.core.llm

Is there a circular import? If yes, how do I fix it?
```

**Why it saves tokens:**
- Direct question format
- LLM can answer yes/no with reasoning
- If yes, LLM suggests refactor without code

---

### Token-Saving Tips in General

1. **Provide context upfront** (structure, file layout)
   - Saves: 50-100 tokens per prompt
   
2. **Use clear input/output format** (list, table, code)
   - Saves: 30-50 tokens per prompt
   
3. **Ask specific questions** ("How do I fix?", not "Help me migrate")
   - Saves: 20-30 tokens per prompt
   
4. **Reference previous context** ("Using the structure from above")
   - Saves: 100+ tokens by avoiding re-explanation

5. **Break large tasks into small prompts**
   - Cheaper to run 3 cheap prompts than 1 expensive prompt
   - Each prompt: ~50-200 tokens (vs. 1000+ for big ones)

**Total possible savings: 500+ tokens per 5-prompt interaction** ✅

---

## Part 5: Prompt to Use When Stuck

**If you get completely stuck and need to ask Claude/ChatGPT for help:**

### Unified Prompt (Use This)

```
I'm migrating a RAG bootcamp codebase to production structure.

CURRENT STATE:
✅ All 5 data integrity fixes merged
✅ All 6 security hardening layers added
✅ All 57 tests passing
✅ Docker works locally
❓ Now migrating structure (bootcamp → production)

CURRENT STRUCTURE (OLD):
src/
├── api_Nishitha.py
├── core/
│   ├── agent_Nishitha.py
│   ├── hardening_Nishitha.py
│   ├── query_router_Nishitha.py
│   ├── retriever.py
│   └── llm.py

TARGET STRUCTURE (NEW):
src/
├── api/main.py
├── agents/langgraph_agent.py
├── core/
│   ├── database/connection.py
│   ├── security/pii_redaction.py
│   ├── security/audit.py
│   └── llm/provider.py
└── utils/config.py

MIGRATION STEPS COMPLETED:
1. ✅ Created new directories
2. ✅ Created config.py (src/utils/config.py)
3. ❌ [STUCK HERE]

PROBLEM: [DESCRIBE WHAT'S NOT WORKING]

What should I do next? Show me exact commands/code.
```

**This prompt gives LLM:**
- Full context (what's done, what's not)
- Clear before/after
- Exact error (if any)
- LLM can give you exact fix without asking clarifications

**Expected response time: ~30 seconds**  
**Expected token cost: 500-800 tokens**  
**Expected accuracy: 95%+**

---

## Part 6: Final Checklist

### Before Committing Migration

```bash
# Run this checklist EXACTLY
echo "=== FINAL MIGRATION CHECKLIST ==="

# 1. No old files
echo "1. Checking for old files..."
find . -name "*_Nishitha.py" -o -name "*_BALU.py" | tee /tmp/old_files.txt
if [ $(wc -l < /tmp/old_files.txt) -eq 0 ]; then
  echo "   ✅ No old files found"
else
  echo "   ❌ FAIL: Old files still exist"
  exit 1
fi

# 2. All imports work
echo "2. Checking imports..."
python -c "
from src.api.main import app
from src.agents.langgraph_agent import run_agentic_query
from src.agents.query_router import route_query
from src.core.database.connection import get_db
from src.core.security.pii_redaction import PIIRedactor
from src.core.security.audit import AuditLogger
from src.utils.config import settings
print('✅ All imports work')
" || { echo "❌ FAIL: Import error"; exit 1; }

# 3. Tests pass
echo "3. Running tests..."
pytest tests/ -q --tb=no || { echo "❌ FAIL: Tests failed"; exit 1; }
echo "   ✅ All tests pass"

# 4. No hardcoded paths
echo "4. Checking for hardcoded paths..."
HARDCODED=$(grep -r '"data/' src/ | grep -v "\.pyc" | wc -l)
if [ "$HARDCODED" -eq "0" ]; then
  echo "   ✅ No hardcoded paths in src/"
else
  echo "   ❌ FAIL: Found $HARDCODED hardcoded paths"
  exit 1
fi

# 5. Config works
echo "5. Testing config..."
python -c "from src.utils.config import settings; print(f'   ✅ Config: {settings.ENVIRONMENT}')"

# 6. Docker runs
echo "6. Testing Docker..."
docker-compose up -d > /dev/null 2>&1
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
  echo "   ✅ Docker API responds"
  docker-compose down > /dev/null 2>&1
else
  echo "   ❌ FAIL: Docker API not responding"
  docker-compose down > /dev/null 2>&1
  exit 1
fi

# 7. Git status clean
echo "7. Checking git status..."
if [ -z "$(git status --porcelain)" ]; then
  echo "   ✅ All changes staged"
else
  echo "   ⚠️  Unstaged changes exist (may be OK if intentional)"
fi

echo ""
echo "=== ✅ MIGRATION COMPLETE ==="
echo "Ready to commit and push!"
```

---

## Summary

You now have:

1. ✅ **Step-by-step migration guide** (8 phases)
2. ✅ **Common mistakes to avoid** (6 mistakes + fixes)
3. ✅ **Token-saving tips** (save 500+ tokens per interaction)
4. ✅ **Prompts to use when stuck** (copy-paste ready)
5. ✅ **Final checklist** (bash script)

**Total time to complete migration: 3-4 hours**

**Next step after this:** Production deployment (follow deployment runbook)
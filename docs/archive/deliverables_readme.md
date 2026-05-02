# RAG Bootcamp Deliverables - Audit Report

This directory contains the submission-grade audit and deliverables package for the RAG Bootcamp project, focusing on the progress from the `main` branch to the `balu` branch.

## Directory Structure

- **`verdict_summary.md`**: A full 16-item checklist of the system's status with technical notes and code references.
- **`course_corrections_status.md`**: An evaluation of the 8 required actions from the Day 0 review.
- **`next_submission_evidence.md`**: Validation of the 5 required submission deliverables with an execution guide for missing items.
- **`branch_diff_analysis.md`**: A technical comparison between the `main` and `balu` branches.

## Key Accomplishments in `balu` Branch

1. **Production Infrastructure:** Migrated from in-memory ChromaDB to a containerized PostgreSQL + pgvector vector store.
2. **Corrected Evaluation:** Fixed a critical bug where the model was being evaluated against its own output.
3. **Real Data Integration:** Implemented a PDF ingestion pipeline that has successfully loaded 861 chunks of Indian Railways GCC data.
4. **Resilient LLM Access:** Developed a 4-provider fallback chain (Groq, OpenRouter, Cerebras, Google) with automatic failover.
5. **Modular Architecture:** Refactored the codebase into a maintainable `src/` package structure.

## Quick Start: Running the Audited Pipeline

### 1. Start the Infrastructure
```bash
docker compose up -d
```

### 2. Ingest Data
```bash
python scripts/ingest_data.py
```

### 3. Run Evaluation
```bash
python scripts/run_experiments.py --exp-name audit_test
```

## Submission Readiness
The system has achieved an **11/16 PASS** score on the requirements checklist. While the core "plumbing" and infrastructure are now excellent, further work is needed on **UMAP visualization**, **comparative chunking metrics**, and **hybrid search** (pg_trgm) to reach a 100% submission-grade state.

---
**Reviewer:** Senior Software Engineer / RAG Specialist  
**Date:** April 25, 2026

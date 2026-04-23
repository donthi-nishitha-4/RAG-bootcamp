# RAG Bootcamp Setup (No-GPU)

## Status

Day 0 setup completed using CPU-based components and free API services.

---

## Overview

This repository contains a Retrieval-Augmented Generation (RAG) pipeline built as part of the bootcamp setup phase.

The system uses cloud LLM APIs and local CPU-based models to simulate a full RAG workflow.

---

## Architecture

* **Embeddings:** sentence-transformers (CPU)
* **Vector Store:** ChromaDB (temporary)
* **Reranking:** cross-encoder (CPU)
* **LLM:** Groq (primary), OpenRouter (fallback)
* **Evaluation:** LLM-based scoring + MLflow tracking

---

## RAG Flow

1. Convert query → embedding
2. Retrieve top-K documents (ChromaDB)
3. Rerank results (cross-encoder)
4. Generate answer using LLM (with fallback)
5. Evaluate output (faithfulness, relevance)
6. Log metrics (MLflow)

---

## What is Implemented

* Groq LLM (primary)
* OpenRouter fallback (basic fallback chain)
* sentence-transformers embeddings (CPU)
* cross-encoder reranking (CPU)
* ChromaDB vector store (temporary)
* End-to-end RAG pipeline
* LLM-based evaluation (faithfulness, relevance)
* MLflow experiment tracking
* `.env`-based secret management
* Docker setup

---

## What is NOT Implemented (Pending)

* pg_trgm (BM25 search)
* Apache AGE (graph layer)
* HuggingFace API usage for embeddings (optional)

---

## Why ChromaDB is Used

PostgreSQL + pgvector requires Linux/WSL setup.
Current Windows environment caused installation issues.

ChromaDB is used temporarily for local CPU-based prototyping.

---

## Setup Instructions

```bash
pip install -r requirements.txt
python rag_chroma.py
```

---

## Environment Variables

Create `.env` file:

```
GROQ_API_KEY=your_key
OPENROUTER_API_KEY=your_key
HF_TOKEN=optional
```

---

## Docker

```bash
docker build -t rag-pipeline .
docker run --env-file .env rag-pipeline
```

---

## TODO (Next Steps)

* Move to Linux/WSL for full bootcamp compatibility
* Setup PostgreSQL + pgvector
* Replace ChromaDB with pgvector
* Add BM25 (pg_trgm)
* Add full fallback chain (Cerebras, Google AI Studio)
* Add API layer (FastAPI)
* Improve logging and monitoring

---

## Note

This repository focuses only on completing the **Day 0 setup checklist**.
Further experiments and optimizations are not included.

---

## Test Results

Successfully loaded 485 chunks from real Indian Railways GCC data into PostgreSQL using pgvector.

**Query:** "What is the procedure for Security Deposit?"

**Output:**
> The procedure for Security Deposit is as follows:
> 
> 1. **Refund of Security Deposit**: The Security Deposit will be returned to the Contractor along with or after Final Payment, Execution of Final Supplementary Agreement, and Maintenance Certificate issued.
> 2. **Forfeiture of Security Deposit**: If the contract is rescinded, the Security Deposit will be retained/encashed by the Railways.
> 3. **Submission of alternative security**: Cash, Term Deposit Receipt, or Bank Guarantee can be submitted.

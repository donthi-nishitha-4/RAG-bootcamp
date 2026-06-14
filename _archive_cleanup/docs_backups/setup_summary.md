# Bootcamp Setup Summary

## Bootcamp Requirements

The bootcamp required setting up a full RAG system with the following components:

* Groq as primary LLM
* Fallback chain (multi-provider)
* CPU embeddings (sentence-transformers)
* Cross-encoder reranking
* Vector database (PostgreSQL + pgvector)
* ChromaDB only for prototyping
* End-to-end RAG pipeline
* Evaluation (RAGAS / LLM-based)
* MLflow tracking
* Secure environment variables (.env, no hardcoded keys)

---

## What is Completed

The following components have been successfully implemented:

* Groq LLM (primary generation)
* OpenRouter fallback (basic fallback chain implemented)
* sentence-transformers embeddings (CPU-based)
* cross-encoder reranking (CPU-based)
* ChromaDB vector store (used as temporary replacement)
* End-to-end RAG pipeline (retrieval → rerank → generation)
* LLM-based evaluation (faithfulness, relevance)
* MLflow experiment tracking
* `.env`-based secret management (no hardcoded keys)
* Docker setup for reproducibility

---

## What is Not Implemented / Failed

The following components are pending or not completed:

* PostgreSQL + pgvector (installation failed on Windows)
* pg_trgm (BM25-based retrieval)
* Apache AGE (graph-based retrieval layer)
* Full fallback chain (Cerebras, Google AI Studio not added)
* HuggingFace API-based embedding usage (optional)

---

## Why ChromaDB is Used

PostgreSQL + pgvector requires a Linux/WSL-based setup.
Due to Windows environment limitations, installation was not successful.

ChromaDB is used as a temporary local vector store for CPU-based prototyping.

---

## Current Status

* Core RAG setup is complete
* System runs end-to-end
* Retrieval, reranking, generation, evaluation, and tracking are functional
* Infrastructure components (pgvector stack) are pending

---

## Notes

* This implementation focuses only on completing the **Day 0 setup checklist**
* It is not a production-ready system yet
* The system is structured to easily migrate to PostgreSQL + pgvector later
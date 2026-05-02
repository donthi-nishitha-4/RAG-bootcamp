# RAG Pipeline Setup - Complete Step-by-Step Guide

## Overview

This document explains how we set up a **Naive RAG (Retrieval-Augmented Generation) Pipeline** from scratch. The pipeline uses:
- **Embeddings**: sentence-transformers (CPU-based)
- **Vector Store**: ChromaDB
- **Reranking**: Cross-encoder
- **LLM**: Groq (with OpenRouter fallback)
- **Evaluation**: LLM-based scoring
- **Tracking**: MLflow

---

## Step 1: Project Structure Review

### What We Had
```
aipms-rag-bootcamp/
├── Dockerfile
├── rag_chroma.py          # Main RAG pipeline
├── rag_eval_pipeline.py   # Evaluation script
├── rag_mlflow.py          # MLflow tracking
├── ragas_groq.py          # RAGAS evaluation
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── docs/
│   └── setup_summary.md
├── .env                   # Environment variables
└── .env.example           # Template for .env
```

### Why
Understanding the existing project structure before making changes helps identify what components are already in place and what needs to be added.

---

## Step 2: Check Existing Python Environment

### Command Used
```bash
python --version
```

### What & Why
We verified Python was installed. The project requires Python 3.11+ for compatibility with all dependencies.

---

## Step 3: Install Docker

### Problem Encountered
Initially, Docker was not installed on the system.

### Commands Used
```bash
# Step 3a: Remove problematic VS Code repository (caused GPG errors)
sudo rm /etc/apt/sources.list.d/vscode.list

# Step 3b: Update package list
sudo apt update

# Step 3c: Install Docker
sudo apt install -y docker.io
```

### What & Why
- **Docker** is needed to containerize the RAG pipeline
- The VS Code repository had GPG key issues, so we removed it
- `docker.io` is the official Docker package for Ubuntu

### Verification
```bash
docker --version
# Output: Docker version 29.1.3
```

---

## Step 4: Start Docker Service

### Command Used
```bash
sudo service docker start
```

### What & Why
The Docker daemon needs to be running before we can build or run containers. This starts the Docker service in the background.

---

## Step 5: Add User to Docker Group (Permission Fix)

### Problem
Regular user couldn't access Docker socket - "permission denied while trying to connect to the docker API"

### Command Used
```bash
sudo usermod -aG docker $USER
```

### What & Why
- By default, only root and docker group members can access Docker
- Adding the current user to the docker group allows running Docker without sudo
- Requires logout/login to take effect

---

## Step 6: Build Docker Image

### Command Used
```bash
sudo docker build -t rag-pipeline .
```

### What & Why
- `-t rag-pipeline` tags the image with name "rag-pipeline"
- `.` tells Docker to use the current directory (where Dockerfile is)
- This builds the container image with all Python dependencies

### Dockerfile Content
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "rag_chroma.py"]
```

### Build Output (Success)
```
[+] Building 542.6s (10/10) FINISHED
 => naming to docker.io/library/rag-pipeline:latest
 => unpacking to docker.io/library/rag-pipeline:latest
```

---

## Step 7: Verify Docker Image

### Command Used
```bash
sudo docker images | grep rag-pipeline
```

### What & Why
Confirms the image was created successfully and shows its details.

### Output
```
rag-pipeline:latest   65dc5dceb06b       9.55GB         3.18GB
```

---

## Step 8: Run Docker Container

### Command Used
```bash
sudo docker run --env-file .env rag-pipeline
```

### What & Why
- `--env-file .env` passes environment variables (API keys) to the container
- `rag-pipeline` is the image name to run
- This executes the RAG pipeline inside the container

### Output (Success)
```
[INFO] Models loaded
[INFO] Chroma initialized
[INFO] Documents stored in Chroma
[INFO] Running RAG with Chroma + Fallback...

[INFO] Top-K retrieved:
1. AI is used in healthcare for diagnosis
2. Python is widely used for AI development
3. Deep learning uses neural networks

[INFO] After reranking:
1. AI is used in healthcare for diagnosis
2. Python is widely used for AI development

[INFO] Used provider: groq

[FINAL ANSWER]
AI is used in healthcare for diagnosis. This means that AI systems, which can be 
developed using programming languages like Python, are utilized to help doctors 
and medical professionals identify and determine the cause of a patient's 
symptoms or condition.
```

---

## How the RAG Pipeline Works

### Architecture Flow
```
User Query
    │
    ▼
┌─────────────────┐
│  Embedding      │  ← sentence-transformers (all-MiniLM-L6-v2)
│  Generation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Search  │  ← ChromaDB (top-K = 3)
│  (Retrieval)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Reranking      │  ← Cross-encoder (final-K = 2)
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generation │  ← Groq (llama-3.3-70b-versatile)
│                 │     with OpenRouter fallback
└────────┬────────┘
         │
         ▼
    Final Answer
```

### Each Component Explained

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Embeddings** | sentence-transformers | Convert text to numerical vectors |
| **Vector Store** | ChromaDB | Store and search document vectors |
| **Reranking** | Cross-encoder | Reorder retrieved results by relevance |
| **LLM** | Groq + OpenRouter | Generate final answer from context |
| **Evaluation** | LLM-based | Score faithfulness and relevance |
| **Tracking** | MLflow | Log experiments and metrics |

---

## Quick Reference Commands

```bash
# Build the Docker image
sudo docker build -t rag-pipeline .

# Run the container
sudo docker run --env-file .env rag-pipeline

# List Docker images
sudo docker images

# Check Docker version
docker --version

# Start Docker service
sudo service docker start
```

---

## Environment Variables Required

Create a `.env` file with:
```
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## Summary

1. ✅ Installed Docker on Ubuntu
2. ✅ Created Docker image with all dependencies
3. ✅ Ran RAG pipeline in container
4. ✅ Verified pipeline works end-to-end

The pipeline successfully:
- Loads embedding model
- Initializes ChromaDB vector store
- Stores sample documents
- Retrieves relevant documents
- Reranks results
- Generates answer using Groq LLM

---

*Document created: April 21, 2026*
*Project: aipms-rag-bootcamp*
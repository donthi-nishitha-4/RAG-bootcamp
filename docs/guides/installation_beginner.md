# 🚀 Windows Setup Guide (Docker Desktop + WSL2)

This guide will help you run the production-ready RAG system on Windows with minimal manual setup using Docker Desktop and WSL2.

---

## 📋 Prerequisites

1. **Docker Desktop**: [Download and Install](https://www.docker.com/products/docker-desktop/)
2. **WSL2 Backend**: Ensure "Use the WSL 2 based engine" is checked in Docker Desktop Settings (**Settings > General**).
3. **API Keys**: You will need a Groq API Key (get it [here](https://console.groq.com/keys)).

---

## 🛠 Step-by-Step Setup

### 1. Prepare Environment Variables
Open the project folder in VS Code or File Explorer. Create a file named `.env` in the root directory and add your keys:

```env
GROQ_API_KEY=your_actual_key_here
# Optional fallbacks
OPENROUTER_API_KEY=your_key
CEREBRAS_API_KEY=your_key
GEMINI_API_KEY=your_key
```

### 2. Launch the System
Open a terminal (PowerShell, CMD, or Git Bash) in the project root and run:

```bash
docker-compose up -d --build
```

- This will automatically:
  - Start the **PostgreSQL + pgvector** database.
  - Build the **RAG Pipeline** container.
  - Wait for the database to be healthy before starting.

### 3. Ingest Data (First Time Only)
To load the Indian Railways GCC documents into your vector database, run:

```bash
docker exec -it rag-app python scripts/ingest_data.py
```

### 4. Run Experiments / Evaluation
To see the RAG system in action and view evaluation scores:

```bash
docker exec -it rag-app python scripts/run_experiments.py
```

---

## 📂 Viewing Results on Windows
Since we use **Docker Volumes**, all files generated inside the container are automatically synced to your Windows folder:
- **Experiment Logs**: Check the `experiments/` folder.
- **Evaluation History**: Check `docs/evaluation_results.md`.
- **Processed Chunks**: Check `data/processed/`.

---

## ⚠️ Common Windows Issues & Fixes

### 1. "Port 5432 is already in use"
**Cause:** You have a local PostgreSQL installed on Windows.
**Fix:** Stop the local service (Search for "Services" > "postgresql" > Stop) or change the port in `docker-compose.yml` (e.g., `- "5433:5432"`).

### 2. "Line Endings (CRLF vs LF)"
**Cause:** Git on Windows sometimes changes file line endings, which breaks shell scripts in Linux containers.
**Fix:** The Dockerfile and Python scripts are designed to be cross-platform, but if you encounter issues, use VS Code to change "CRLF" to "LF" for the specific file in the bottom right corner.

### 3. "Volume sharing denied"
**Cause:** Docker Desktop doesn't have permission to access your drive.
**Fix:** Go to **Settings > Resources > File Sharing** in Docker Desktop and ensure your project drive (usually C:) is shared.

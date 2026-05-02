# 🌍 Multi-Platform Setup Guide (Windows & WSL2)

This guide provides step-by-step instructions for running the AI-PMS RAG Bootcamp project on **Windows 10/11** and **WSL2 (Windows Subsystem for Linux)**.

---

## 🏗️ 1. Infrastructure Overview

The project uses **Docker Compose** to manage two core services:
1.  **`db` (PostgreSQL + pgvector)**: The vector database for storing embeddings.
2.  **`app` (Python)**: The RAG pipeline and evaluation logic.

---

## 🔑 2. Environment Variables Configuration

The system relies on a `.env` file for all configurations. This is critical for cross-platform compatibility.

### Setting up the `.env` file
1.  In the project root, rename `.env.example` to `.env`.
2.  Open `.env` and configure the following variables:

| Variable | Recommended Value | Description |
| :--- | :--- | :--- |
| **`GROQ_API_KEY`** | `your_key` | Primary LLM provider. |
| **`OPENROUTER_API_KEY`** | `your_key` | Secondary LLM provider. |
| **`DB_HOST`** | `127.0.0.1` | Use `127.0.0.1` for local terminal scripts; Docker automatically uses `db`. |
| **`DB_PORT`** | `5433` | Host port to avoid conflict with local PostgreSQL. |
| **`DB_USER`** | `rag_user` | Database username. |
| **`DB_PASSWORD`** | `rag_password` | Database password. |
| **`DB_NAME`** | `rag_bootcamp` | Database name. |

> [!IMPORTANT]
> **Host Configuration**: When running scripts from your **local terminal** (Windows or WSL), use `DB_HOST=127.0.0.1`. When the code runs **inside Docker**, it automatically uses `DB_HOST=db`.

---

## 🪟 3. Windows Native Setup (Docker Desktop)

Use this method if you prefer working directly in PowerShell or Command Prompt.

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- Ensure **Git for Windows** is installed.

### Setup Steps
1.  **Clone the Repo**: `git clone <repo_url>`
2.  **Configure `.env`**: Follow the steps in Section 2.
3.  **Start Services**:
    ```powershell
    docker-compose up -d
    ```
4.  **Install Python Dependencies (Local)**:
    If you want to run scripts from your PowerShell terminal:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

---

## 🐧 4. WSL2 Setup (Highly Recommended)

WSL2 provides a native Linux environment on Windows and is significantly faster for I/O operations.

### Prerequisites
- Install a Linux distribution (e.g., **Ubuntu**) via the Microsoft Store.
- Enable **WSL Integration** in Docker Desktop: `Settings > Resources > WSL Integration > Enable for your distro`.

### Setup Steps
1.  **Open Ubuntu Terminal**.
2.  **Move project to WSL filesystem**:
    *Avoid* `/mnt/c/`. Instead, clone into your Linux home directory:
    ```bash
    cd ~
    git clone <repo_url>
    cd aipms-rag-bootcamp
    ```
3.  **Configure `.env`**: `cp .env.example .env && nano .env`
4.  **Start Docker Compose**:
    ```bash
    docker-compose up -d
    ```
5.  **Local Python Setup**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

---

## 🛠️ 5. Common Troubleshooting

### Port Conflicts
If you see an error like `Bind for 0.0.0.0:5433 failed: port is already allocated`:
- Change `DB_PORT` in your `.env` to another value (e.g., `5434`).
- Restart with `docker-compose up -d`.

### CRLF vs LF (Line Endings)
Windows uses `\r\n` (CRLF) while Linux uses `\n` (LF).
- If scripts fail in WSL with strange characters, run: `sed -i 's/\r$//' filename.py`.
- **Tip**: Set your VS Code "End of Line" to `LF` for this project.

### Database Connection Refused
If `psql` or your scripts can't connect:
- Ensure the container is healthy: `docker ps`.
- Verify `DB_HOST` is `127.0.0.1` (for local) and `DB_PORT` matches your `.env`.

---

## 🚀 6. Running the Pipeline

Once set up, run these commands in order from your terminal (WSL or PowerShell):

1.  **Ingest Data**: `python scripts/ingest_data.py`
2.  **Run Experiments**: `python scripts/run_experiments.py`
3.  **Check Results**: View the `experiments/` folder.

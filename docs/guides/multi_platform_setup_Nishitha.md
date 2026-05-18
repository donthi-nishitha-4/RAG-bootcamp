# 🌍 Multi-Platform Setup Guide (Windows & WSL2)

This guide provides step-by-step instructions for setting up, configuring, and running the AI-PMS RAG Bootcamp project on **WSL2 (Windows Subsystem for Linux)** and native **Windows 10/11**.

---

## 🏗️ 1. Infrastructure Overview

The RAG application utilizes **Docker Compose** to run its external services:
1. **`db` (PostgreSQL + pgvector)**: Out-of-the-box relational vector database supporting hybrid search via `pgvector` embeddings and `pg_trgm` trigram BM25-like search.
2. **`app` (Python)**: Local execution environment containing embedding pipelines, retrieval optimization, failure modes, and automated Ragas evaluation.

---

## 🔑 2. Environment Variables (`.env`) Configuration

The system reads configurations from a `.env` file located in the root of the project.

### 📝 Step-by-Step `.env` Setup
1. Copy the template to create your active `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in your editor (e.g., `nano .env` or via VS Code) and configure the variables.

### 📋 Comprehensive `.env` Variable Dictionary (Matching Active Setup)

| Environment Variable | Required/Optional | Active Configured Value | Detailed Description & Purpose |
| :--- | :--- | :--- | :--- |
| `GROQ_API_KEY` | **Required (Primary)** | `gsk_...` | API key for Groq. Powers the primary LLM pipeline (`llama-3.3-70b-versatile`). |
| `OPENROUTER_API_KEY` | **Highly Recommended** | `sk-or-v1-...` | API key for OpenRouter. First-tier fallback if Groq hits rate-limits. |
| `CEREBRAS_API_KEY` | *Optional (Fallback)* | *(blank)* | API key for Cerebras. Second-tier fast LLM fallback. |
| `GEMINI_API_KEY` | *Optional (Fallback)* | `AIzaSy...` | API key for Google Gemini. Third-tier fallback. |
| `DB_HOST` | **Required** | `127.0.0.1` | **Crucial:** Set to `127.0.0.1` when executing python scripts from local WSL terminal. In Docker, it dynamically overrides to `db`. |
| `DB_PORT` | **Required** | `5433` | Port exposed on host machine to prevent conflicts with a default postgres daemon running locally on port `5432`. |
| `DB_USER` | **Required** | `postgres` | Superuser credential configured in the active environment to prevent privilege issues. |
| `DB_PASSWORD` | **Required** | `postgres` | Password for active PostgreSQL user. |
| `DB_NAME` | **Required** | `postgres` | Database name utilized for vector and text indexing. |

---

## 🏗️ 3. Container Network & Port Mapping Decoded

Understanding how Docker interacts with your environment settings is key to running this modular RAG successfully:

```
┌────────────────────────────────────────────────────────┐
│                   WSL2 HOST MACHINE                     │
│                                                        │
│  Local scripts (ingest_data.py, run_experiments.py)    │
│  connect to database via:                              │
│  DB_HOST=127.0.0.1   DB_PORT=5433                      │
└──────────────────────────┬─────────────────────────────┘
                           │ Port-Forwarding (5433:5432)
                           ▼
┌────────────────────────────────────────────────────────┐
│                DOCKER COMPOSE BRIDGE NETWORK           │
│                                                        │
│  [db] container (pgvector)                             │
│       Exposed internally on port 5432                  │
│       Exposed externally on port 5433                  │
│                                                        │
│  [app] container (Python running pipeline)             │
│       Connects to pgvector container via internal DNS  │
│       DB_HOST=db   DB_PORT=5432                        │
└────────────────────────────────────────────────────────┘
```

### 1. The `Dockerfile` Environment Defaults
The `Dockerfile` baked-in values ensure that if the app is run fully inside the container network, it connects to standard PostgreSQL ports:
*   `ENV DB_HOST=db` — Resolves to the container host name using Docker’s bridge network DNS.
*   `ENV DB_PORT=5432` — Standard container port for PostgreSQL.

### 2. The `docker-compose.yml` Overrides
The `docker-compose.yml` maps host port `5433` to container port `5432`:
*   `ports: - "${DB_PORT:-5433}:5432"`: This exposes the database to local WSL/Windows scripts on port `5433` while protecting local port `5432`.
*   Inside the `app` container service, standard settings are hardcoded to ignore `.env` host settings:
    ```yaml
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    ```
    This ensures that Docker-to-Docker connections work out-of-the-box, regardless of local script settings!

---

## 🐧 4. WSL2 Setup — *Highly Recommended*

WSL2 is the recommended environment for the AI-PMS RAG Bootcamp, providing a native Linux environment with up to **10x faster disk I/O performance** compared to Windows mounts.

### 🏃 Step-by-Step Installation & Execution in WSL2

#### 1. Move to the Linux Native Filesystem
> [!IMPORTANT]
> **Performance Warning**: **DO NOT** run the project under `/mnt/c/...` (Windows mount). File translation between Windows and WSL2 causes major bottlenecks. Clone and build the project in the native Linux ext4 path (e.g., in your home directory `~`).

```bash
cd ~
git clone <your-repository-url>
cd aipms-rag-bootcamp
```

#### 2. Create Python Virtual Environment & Install Dependencies
Initialize a fresh Python virtual environment inside WSL2:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Spin up Database Services
Launch the PostgreSQL and `pgvector` container:
```bash
docker-compose up -d
docker ps
```

#### 4. Verify Database and Ingest Data
```bash
python db_check.py
python scripts/ingest_data.py
```

#### 5. Run Evaluations & Experiments
```bash
python scripts/run_experiments.py
python eval_ragas.py
```

---

## 🪟 5. Native Windows Setup (Powershell / CMD)

If you must run natively on Windows without WSL:

1. Open PowerShell in administrative mode.
2. Clone and enter project:
   ```powershell
   git clone <your-repository-url>
   cd aipms-rag-bootcamp
   ```
3. Configure `.env`:
   ```powershell
   copy .env.example .env
   ```
4. Start Docker Compose: `docker-compose up -d`
5. Set up virtual environment and install packages:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
6. Ingest and run:
   ```powershell
   python scripts/ingest_data.py
   python scripts/run_experiments.py
   ```

---

## 🧠 6. Historical `.env` & Network Connection Debugging Log

During the development and testing phases, we encountered several distinct database connection and environment challenges. Capturing these fixes provides vital technical context for final evaluation:

### 🔍 Case Study 1: The "could not translate host name 'db'" Crisis
*   **Symptom**: When running local python ingestion and test scripts (`scripts/ingest_data.py` or `db_check.py`) directly from the WSL terminal, the program failed with:
    `[ERROR] DB Connection failed: could not translate host name "db"`
*   **Root Cause**: The `.env` file originally contained `DB_HOST=db`. The hostname `db` is an internal Docker Compose bridge network DNS alias. Local terminals outside of the Docker container environment cannot resolve `db` to any IP address.
*   **Resolution**: Set `DB_HOST=127.0.0.1` in the local `.env` file. This directs local terminal scripts to connect via the host loopback adapter. The `docker-compose.yml` `app` service is configured with a hardcoded `DB_HOST=db` environment override, ensuring the Dockerized runtime remains unaffected.

### 🔍 Case Study 2: Host PostgreSQL Port Clash (`5432` vs `5433`)
*   **Symptom**: Running `docker-compose up -d` resulted in a port allocation error:
    `Bind for 0.0.0.0:5432 failed: port is already allocated`
*   **Root Cause**: The host system (or WSL) was already running a native PostgreSQL service on the standard port `5432`, blocking the docker container from binding to it.
*   **Resolution**: Exposed the docker pgvector service externally on host port `5433` (via mapping `5433:5432`), while retaining port `5432` inside the private docker container network. The `.env` file was updated to `DB_PORT=5433` for all local terminal-run scripts.

### 🔍 Case Study 3: The Silent Early Ingestion Exit
*   **Symptom**: Retrieval failed with `relation "rag_documents" does not exist`, even after running `python scripts/ingest_data.py`.
*   **Root Cause**: The ingestion script previously checked for `data/raw` and exited early without logs if it was missing. The actual text documents were located in `data/gcc` and `data/dmrc`. This prevented `init_pgvector()` from ever executing.
*   **Resolution**: Refactored `scripts/ingest_data.py` to recursively scan all subdirectories under `data/` using `os.walk()`, allowing seamless discovery and chunk ingestion from multiple folders simultaneously.

### 🔍 Case Study 4: RAGAS Evaluation NaN Scores & API Rate Limits (429)
*   **Symptom**: Automated RAGAS testing raised rate-limiting exceptions or outputted `NaN` scores.
*   **Root Cause**: Groq API rate limits were frequently breached due to intensive token consumption during grading cycles.
*   **Resolution**:
    1. Switched RAGAS evaluation embeddings to a local `all-MiniLM-L6-v2` instance (running entirely on local CPU via `LangchainEmbeddingsWrapper`), saving massive token overhead.
    2. Implemented a robust sequential LLM fallback chain in `src/core/llm.py` (**Groq ➔ OpenRouter ➔ Cerebras ➔ Gemini**) to dynamically recover if rate limits (429) are encountered.
    3. Replaced deprecated RAGAS API calls to ensure compliance with v0.2+ metric classes.


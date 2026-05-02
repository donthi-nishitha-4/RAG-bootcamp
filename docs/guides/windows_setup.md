# Run on Windows (Docker Desktop + WSL2)

> [!TIP]
> This guide is now consolidated into the [Detailed Multi-Platform Setup Guide](multi_platform_setup.md). Please refer to that for the most up-to-date instructions.

This project has been optimized to run seamlessly on Windows systems using Docker Desktop with the WSL2 backend.

## Prerequisites

1. **Windows 10/11**
2. **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
3. **WSL2** (Windows Subsystem for Linux):
   - Open PowerShell as Administrator and run: `wsl --install`
   - Ensure Docker Desktop is configured to use the WSL2 based engine (Settings -> General -> Check "Use the WSL 2 based engine").

## Step-by-Step Setup

### 1. Clone the Repository
Open a terminal (preferably inside a WSL2 Ubuntu distro, e.g., using Windows Terminal) and clone the project:
```bash
git clone <your-repo-url>
cd aipms-rag-bootcamp
```
*(Note: Running this inside the WSL filesystem like `~/projects/aipms-rag-bootcamp` is up to 10x faster than running it on the Windows filesystem `/mnt/c/...`)*

### 2. Configure Environment Variables
You must set up your API keys before running the container. Copy the example environment file:
```bash
cp .env.example .env
```
Open the `.env` file in Notepad or VS Code and add your keys (e.g., Groq, OpenRouter).

### 3. Build and Run the Containers
Run the following command to build the image and start the PostgreSQL (pgvector) database and the RAG app:
```bash
docker compose up -d --build
```
- `-d` runs it in detached mode (in the background).
- `--build` ensures any Windows-specific cache states are refreshed.

### 4. Verify It's Running
To check the logs and ensure the app started correctly:
```bash
docker compose logs -f app
```

## Running Scripts Inside the Container
Because your code is mounted as a volume, you can edit scripts in Windows (e.g., using VS Code), and the container will see the updates instantly.

To manually run an experiment or evaluation script inside the container:
```bash
docker compose exec app python scripts/run_experiments.py
```

## Common Windows Issues & Fixes

**1. "line 1: \r: command not found" or syntax errors**
* **Cause**: Windows uses CRLF (`\r\n`) line endings, while Linux expects LF (`\n`). If you edit bash scripts on Windows, they might get CRLF endings.
* **Fix**: Ensure your IDE (like VS Code) is set to save files with `LF` line endings. You can also fix a file by running `dos2unix filename` inside WSL.

**2. File Permission or Locking Errors (`__pycache__` issues)**
* **Cause**: Python creating compiled `.pyc` files on a Windows volume mount can cause file locks.
* **Fix**: This has been resolved in the current `Dockerfile` and `docker-compose.yml` by setting `PYTHONDONTWRITEBYTECODE=1`, which stops Python from generating these files.

**3. Docker Compose complains about missing `.env` file**
* **Cause**: You cloned the repo but forgot to create `.env`.
* **Fix**: The compose file is updated to make `.env` optional so the container won't completely crash, but your API calls will fail. Create it using `cp .env.example .env`.

**4. Sluggish Database or Container Performance**
* **Cause**: The project is sitting on your `C:\` drive (`/mnt/c/...`). Cross-OS file sharing is slow.
* **Fix**: Move the project directory inside the WSL filesystem (e.g., `/home/username/aipms-rag-bootcamp`). Docker handles WSL mounts significantly faster than Windows mounts.

# 🚧 BLOCKERS & REQUIREMENTS REGISTER

---

## 1. CRITICAL BLOCKERS (CURRENT & FUTURE)

| ID | Blocker Type | Description | Impact | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **BLK-01** | **TIME** | Creating the **80+ Query Golden Dataset** (manual labeling). | High | Start Day 3. Each student writes 10 queries per day. |
| **BLK-02** | **INFRA** | **Apache AGE** installation on Ubuntu/HPC. Can be complex to build from source. | Medium | Attempt installation on Day 1. Use Mock Graph if it fails. |
| **BLK-03** | **LATENCY** | **Reranking & Agentic RAG** may exceed the 5-second NFR on GPREC hardware. | High | Measure latency from Day 4. Optimize batch sizes. |
| **BLK-04** | **API LIMITS** | **Groq/OpenRouter** rate limits during heavy evaluation runs (Day 9). | Medium | Ensure all 4 fallback providers are active in `.env`. |
| **BLK-05** | **DATA** | Missing **Kaggle Enterprise RAG** dataset files. | Medium | Download and organize in `data/raw/` by Day 2. |

---

## 2. SYSTEM REQUIREMENTS (MANDATORY)

### 💻 Hardware
*   **Ubuntu/WSL**: Min 16GB RAM (32GB preferred for vLLM).
*   **Disk**: 50GB free space (for model weights and Docker volumes).

### 🛠 Software (Ubuntu/WSL Status)
*   **OS**: Ubuntu 22.04.5 LTS ✅ (Verified)
*   **Python**: 3.10.12 ✅ (Verified)
*   **Docker**: 29.4.1 ✅ (Verified)
*   **libmagic**: Installed ✅ (Verified)
*   **poppler-utils**: Installed ✅ (Verified)
*   **tesseract-ocr**: ❌ MISSING (Required for scanned PDFs)
*   **System Libs**: `libmagic-dev` ❌ (May be needed for unstructured)
*   **Python (RAGAS/LangGraph/MLflow)**: ✅ INSTALLED
*   **Python (unstructured)**: ❌ MISSING (Required for advanced parsing)

---

## 3. API KEY STATUS

| Provider | Status | Usage |
| :--- | :--- | :--- |
| **Groq** | ✅ ACTIVE | Primary LLM (Llama 3.3 70B) |
| **OpenRouter** | ✅ ACTIVE | Primary Fallback |
| **Cerebras** | ❌ MISSING | Secondary Fallback (Ultra-fast Llama 3.1) |
| **Google AI Studio** | ❌ MISSING | Tertiary Fallback (Gemini 1.5 Pro) |

---

## 4. INSTALLATION CHECKLIST (DAY 1)

1.  **Postgres**: Must have `vector` and `pg_trgm` extensions.
2.  **vLLM**: (Optional) Only if local GPU is available.
3.  **Python Packages**:
    ```bash
    pip install sentence-transformers cross-encoder psycopg2-binary \
                python-dotenv langgraph ragas mlflow unstructured[pdf]
    ```

---

## 5. ACTION ITEMS FOR TEAM LEAD (BALU)
- [ ] Collect Cerebras and Gemini API keys.
- [ ] Verify `docker-compose` works on the GPREC HPC node.
- [ ] Confirm "Golden Query" assignments for Students E-F.

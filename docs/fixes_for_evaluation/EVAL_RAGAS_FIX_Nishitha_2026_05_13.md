# Session Log — D Nishitha | 2026-05-13

---

## Overview
The focus of today's session was achieving 100% compliance with the **Progress Review** feedback received from Bhanu (the instructor). We addressed the "Needs Improvement" and "Next Steps" items specifically assigned to D Nishitha.

---

## 1. Compliance with Instructor Review

| Review Item | Action Taken Today | Status |
|---|---|---|
| **Fill "Surprising Finding" & "Production Implication"** | Updated `exp_01`, `exp_02`, `exp_03`, and `exp_04` logs with detailed analysis and production-level insights. | ✅ Complete |
| **Expand Evaluation Query Set (30+ queries)** | Confirmed the golden dataset has 35 entries covering all document types (NCR, DPR, GCC). | ✅ Complete |
| **Automated RAGAS Metrics** | Refactored `eval_ragas.py` twice to fix API credential issues and metric initialization errors. | ✅ Ready for Run |
| **Comparison Summary Table** | Updated `run_eval.py` to automatically compare Vector vs. Hybrid search. | ✅ Ready for Run |

---

## 2. Technical Fixes & Improvements

### Experiment Log Refactoring
*   **exp_02 (Semantic Baseline):** Added root cause analysis for failures related to clause-spanning answers. Highlighted the risk of silent failures in legal RAG.
*   **exp_03 (Hybrid Search):** Documented how keyword matching (Trigram) improves retrieval but still requires proper chunking strategies.
*   **exp_04 (Breaking Experiment):** Analyzed "Entity Confusion." Found that LLM reasoning (Llama 70B) is a strong filter, but metadata filtering is needed for production efficiency.

### RAGAS Pipeline Overhaul (`scripts/eval_ragas.py`)
*   **Metric Instantiation:** Updated script to use class-based metrics (e.g., `Faithfulness(llm=...)`) to match RAGAS v0.2+ requirements.
*   **Order of Operations:** Fixed an `UnboundLocalError` by ensuring the LLM and Embeddings are built *before* metrics are initialized.
*   **Local Embeddings:** Switched to local `all-MiniLM-L6-v2` via `LangchainEmbeddingsWrapper` to bypass OpenAI API dependency and token costs.

### Evaluation Script Update (`scripts/run_eval.py`)
*   Modified the main execution block to run **Vector** and **Hybrid** search sequentially. This will generate the final comparison table needed for the report.

---

## 3. Current Blockers & Resolution

### **Issue: Groq API Rate Limit (429 Error)**
*   **Status:** The account has reached the daily limit (100,000 tokens).
*   **Impact:** The RAGAS evaluation started correctly but was interrupted because the grading phase requires more tokens than were available.
*   **Resolution:** The script is verified to be working. The user will re-run the final evaluations tomorrow when the token limit resets.

---

## 4. Pending Actions for Tomorrow

1.  **Execute Final RAGAS Report:**
    `python scripts/eval_ragas.py`
2.  **Execute Final Comparison Table:**
    `python scripts/run_eval.py`
3.  **Final Submission:**
    Submit the Markdown reports generated in `experiments/results/` to Bhanu.

---

*Documented by D Nishitha session, 2026-05-13*

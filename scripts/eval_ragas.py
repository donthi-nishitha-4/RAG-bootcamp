"""
eval_ragas.py — RAGAS Automated Evaluation Pipeline (D Nishitha)
Loads the 30+ golden dataset, runs the RAG pipeline, and evaluates using RAGAS metrics
(faithfulness, answer_relevancy, context_precision, context_recall) via Groq as the LLM.
Results saved to experiments/results/.

Requirements:
  pip install ragas langchain-groq langchain-openai
"""
import sys
import os
import json
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import ask_rag
from src.core.retriever import check_table_exists
from dotenv import load_dotenv

load_dotenv()

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results')
TENANT_ID    = "default_strategy"


def build_ragas_llm():
    """
    Build RAGAS LLM using llm_factory with Groq's OpenAI-compatible endpoint.
    Avoids the deprecated LangchainLLMWrapper.
    """
    try:
        from openai import OpenAI
        from ragas.llms import llm_factory
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not set")
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_key
        )
        llm = llm_factory("llama-3.3-70b-versatile", client=client)
        print("[INFO] RAGAS LLM: Groq via llm_factory (llama-3.3-70b-versatile)")
        return llm
    except Exception as e:
        print(f"[ERROR] Could not build RAGAS LLM: {e}")
        return None


def build_ragas_embeddings():
    """
    Build RAGAS embeddings using local all-MiniLM-L6-v2 (already installed).
    No OpenAI key required.
    """
    try:
        from ragas.embeddings import LangchainEmbeddingsWrapper
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings
        hf_emb = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        print("[INFO] RAGAS Embeddings: local all-MiniLM-L6-v2 (no OpenAI needed)")
        return LangchainEmbeddingsWrapper(hf_emb)
    except Exception as e:
        print(f"[ERROR] Could not build RAGAS embeddings: {e}")
        return None


def run_ragas_evaluation():
    # Pre-flight check
    if not check_table_exists():
        print("[ERROR] rag_documents table is empty. Run: python scripts/ingest_data.py")
        return

    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        raw_dataset = json.load(f)

    # Skip adversarial entries for RAGAS (no meaningful ground_truth available)
    dataset = [item for item in raw_dataset if item.get("source") != "adversarial"]
    print(f"[INFO] Loaded {len(dataset)} non-adversarial entries for RAGAS evaluation.")

    ragas_records = []
    print("[INFO] Running RAG pipeline to collect answers and contexts...")

    for i, item in enumerate(dataset, 1):
        query        = item.get("query", "").strip()
        ground_truth = item.get("expected_answer", "")
        if not query:
            continue

        print(f"  [{i}/{len(dataset)}] {query[:70]}")
        result = ask_rag(query, tenant_id=TENANT_ID)
        answer  = result.get("answer", "")
        context = result.get("context", "")

        ragas_records.append({
            "question":    query,
            "answer":      answer,
            "contexts":    [context] if context else [""],
            "ground_truth": ground_truth,
        })

    # Build RAGAS dataset
    try:
        from datasets import Dataset as HFDataset
        from ragas import evaluate
        from ragas.metrics.collections import faithfulness, answer_relevancy, context_precision, context_recall
    except ImportError as e:
        print(f"[ERROR] RAGAS/datasets not installed: {e}")
        print("Run: pip install ragas datasets")
        return

    hf_dataset = HFDataset.from_list(ragas_records)
    print(f"\n[INFO] RAGAS dataset built with {len(ragas_records)} entries.")
    print(hf_dataset)

    # Build LLM and embeddings wrappers
    ragas_llm = build_ragas_llm()
    if ragas_llm is None:
        print("[ERROR] Could not build RAGAS LLM. Evaluation aborted.")
        return

    ragas_embeddings = build_ragas_embeddings()
    if ragas_embeddings is None:
        print("[ERROR] Could not build RAGAS embeddings. Evaluation aborted.")
        return

    # Run RAGAS evaluation
    print("\n[INFO] Running RAGAS evaluate()...")
    try:
        result = evaluate(
            dataset=hf_dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
            llm=ragas_llm,
            embeddings=ragas_embeddings,
        )
        print("\n[RAGAS SCORES]")
        print(result)

        scores_dict = result.to_pandas().to_dict(orient="records")
    except Exception as e:
        print(f"[ERROR] RAGAS evaluate() failed: {e}")
        # Save the prepared dataset even if evaluation failed — shows pipeline is wired
        scores_dict = ragas_records

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(RESULTS_DIR, f"ragas_eval_{ts}.json")
    with open(json_path, 'w') as f:
        json.dump(scores_dict, f, indent=2, default=str)
    print(f"\n[SAVED] RAGAS results → {json_path}")

    # Markdown summary
    md_path = os.path.join(RESULTS_DIR, f"ragas_eval_{ts}.md")
    try:
        df = result.to_pandas()
        avg_f  = df["faithfulness"].mean()
        avg_ar = df["answer_relevancy"].mean()
        avg_cp = df["context_precision"].mean()
        avg_cr = df["context_recall"].mean()
        md = f"# RAGAS Evaluation — {ts}\n\n"
        md += f"**Tenant:** {TENANT_ID} | **Entries evaluated:** {len(ragas_records)}\n\n"
        md += "## Aggregate Scores\n"
        md += "| Metric | Score |\n|---|---|\n"
        md += f"| Faithfulness | {avg_f:.3f} |\n"
        md += f"| Answer Relevancy | {avg_ar:.3f} |\n"
        md += f"| Context Precision | {avg_cp:.3f} |\n"
        md += f"| Context Recall | {avg_cr:.3f} |\n\n"
        md += "## Per-Query Scores\n"
        md += "| Question | Faithfulness | Answer Relevancy | Context Precision | Context Recall |\n"
        md += "|---|---|---|---|---|\n"
        for _, row in df.iterrows():
            md += (f"| {str(row.get('question',''))[:55]}… "
                   f"| {row.get('faithfulness', 0):.2f} "
                   f"| {row.get('answer_relevancy', 0):.2f} "
                   f"| {row.get('context_precision', 0):.2f} "
                   f"| {row.get('context_recall', 0):.2f} |\n")
        with open(md_path, 'w') as f:
            f.write(md)
        print(f"[SAVED] Markdown → {md_path}")
    except Exception:
        pass  # If RAGAS eval failed, markdown won't have scores — that's fine


if __name__ == "__main__":
    run_ragas_evaluation()

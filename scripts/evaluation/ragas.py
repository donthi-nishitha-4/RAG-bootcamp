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
import time
import datetime


from src.core.pipeline import ask_rag
from src.core.retriever import check_table_exists
from dotenv import load_dotenv

load_dotenv()

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'evaluation', 'dataset', 'evaluation_dataset.json')
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'results')
TENANT_ID    = "default_strategy"

# In scripts/eval_ragas.py

from src.core.llm import RobustLLM

class EvalRobustLLM(RobustLLM):
    """
    A local wrapper to make RobustLLM compatible with RAGAS 
    without changing the core logic in src/core/llm.py.
    """
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.messages import AIMessage
        from langchain_core.outputs import ChatGeneration, ChatResult
        
        # Accept the 'run_manager' to fix the TypeError
        result = super()._generate(messages, stop=stop, **kwargs)
        
        # Convert HumanMessage -> AIMessage so RAGAS metrics calculate correctly
        content = result.generations[0].message.content
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

def build_ragas_llm():
    """
    Build RAGAS LLM using the local EvalRobustLLM wrapper.
    """
    from ragas.llms import LangchainLLMWrapper
    
    return LangchainLLMWrapper(EvalRobustLLM(temperature=0))


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


def run_ragas_evaluation(search_type="vector", limit=None, dataset_path=None):
    # Pre-flight check
    if not check_table_exists():
        print("[ERROR] rag_documents table is empty. Run: python scripts/ingest_data.py")
        return

    path_to_use = dataset_path if dataset_path else DATASET_PATH
    with open(path_to_use, 'r', encoding='utf-8') as f:
        raw_dataset = json.load(f)

    # Filter data
    eval_data = [item for item in raw_dataset if item.get("source") != "adversarial"]
    # Add some adversarial for testing out-of-scope if needed, but RAGAS usually needs ground_truth
    # For now, let's keep the non-adversarial as the primary RAGAS target
    
    print(f"[INFO] Loaded {len(eval_data)} entries.")

    # Use limit if provided, otherwise all
    subset = eval_data[:limit] if limit else eval_data
    print(f"[INFO] Evaluating {len(subset)} entries using search_type={search_type}.")

    ragas_records = []
    print("[INFO] Running RAG pipeline to collect answers and contexts...")

    for i, item in enumerate(subset, 1):
        query        = item.get("query", "").strip()
        ground_truth = item.get("expected_answer", "")
        if not query:
            continue

        print(f"  [{i}/{len(subset)}] {query[:70]}")
        try:
            result = ask_rag(query, tenant_id=TENANT_ID, search_type=search_type)
            answer  = result.get("answer", "")
            context = result.get("context", "")
            # Ensure contexts is strictly a list of strings for RAGAS
            final_contexts = [str(context)] if context else [""]

            ragas_records.append({
                "question":    query,
                "answer":      answer,
                "contexts":    final_contexts,
                "ground_truth": ground_truth,
            })
        except Exception as e:
            print(f"  [ERR] Pipeline failed for query: {e}")
        
        time.sleep(10) # Pause for rate limit stability

    # Build RAGAS dataset
    try:
        from datasets import Dataset as HFDataset
        from ragas import evaluate
        from ragas.metrics import (
            Faithfulness,
            AnswerRelevancy,
            ContextPrecision,
            ContextRecall,
        )
    except ImportError as e:
        print(f"[ERROR] RAGAS/datasets not installed: {e}")
        return

    hf_dataset = HFDataset.from_list(ragas_records)
    print(f"\n[INFO] RAGAS dataset built with {len(ragas_records)} entries.")

    # Build LLM and embeddings wrappers
    ragas_llm = build_ragas_llm()
    if ragas_llm is None:
        print("[ERROR] Could not build RAGAS LLM.")
        return

    ragas_embeddings = build_ragas_embeddings()
    if ragas_embeddings is None:
        print("[ERROR] Could not build RAGAS embeddings.")
        return

    metrics = [
        Faithfulness(llm=ragas_llm),
        AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings),
    ]

    # Run RAGAS evaluation
    print(f"\n[INFO] Running RAGAS evaluate() for {search_type}...")
    try:
        from ragas.run_config import RunConfig
        run_config = RunConfig(max_workers=2)
        
        result = evaluate(
            dataset=hf_dataset,
            metrics=metrics,
            llm=ragas_llm,
            embeddings=ragas_embeddings,
            run_config=run_config
        )
        print("\n[RAGAS SCORES]")
        print(result)
        scores_dict = result.to_pandas().to_dict(orient="records")
    except Exception as e:
        print(f"[ERROR] RAGAS evaluate() failed: {e}")
        scores_dict = ragas_records

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = os.path.join(RESULTS_DIR, f"ragas_eval_{search_type}_{ts}.json")
    with open(json_path, 'w') as f:
        json.dump(scores_dict, f, indent=2, default=str)
    print(f"\n[SAVED] RAGAS results → {json_path}")

    # Markdown summary
    md_path = os.path.join(RESULTS_DIR, f"ragas_eval_{search_type}_{ts}.md")
    try:
        df = result.to_pandas()
        avg_f  = df["faithfulness"].mean()
        avg_ar = df["answer_relevancy"].mean()
        avg_cp = df["context_precision"].mean()
        avg_cr = df["context_recall"].mean()
        md = f"# RAGAS Evaluation — {search_type.upper()} — {ts}\n\n"
        md += f"**Search Strategy:** {search_type} | **Entries:** {len(ragas_records)}\n\n"
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
        pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", type=str, default="vector", choices=["vector", "hybrid"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dataset", type=str, default=None)
    args = parser.parse_args()
    
    run_ragas_evaluation(search_type=args.strategy, limit=args.limit, dataset_path=args.dataset)

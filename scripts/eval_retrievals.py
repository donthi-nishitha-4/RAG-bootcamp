import os
import sys
import json
from statistics import mean

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.pipeline import embed_model
from src.core.llm import query_llm
from src.core.retriever import retrieve_similar, retrieve_hybrid

TOP_K = 5


def load_queries(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Queries file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Expect list of {"query":..., "expected":...}
    return data


import re

def precision_at_k(retrieved_chunks, expected_contexts, k=TOP_K):
    if not expected_contexts:
        return 0.0
    
    # Extract unique words from expected contexts
    expected_text = " ".join(expected_contexts).lower()
    expected_words = set(re.findall(r'\w+', expected_text))
    
    if not expected_words:
        return 0.0
        
    count = 0
    for _, content, _ in retrieved_chunks[:k]:
        content_words = set(re.findall(r'\w+', content.lower()))
        overlap = expected_words.intersection(content_words)
        
        # If at least 30% of the important words overlap, it's a match
        if len(overlap) >= 0.3 * len(expected_words):
            count += 1
            
    return count / k


def run_evaluation(queries, tenant_id='default_strategy', entity_type=None, contract_standard=None):
    baseline_scores = []
    hyde_scores = []
    multi_scores = []

    for item in queries:
        q = item.get('query')
        expected_contexts = item.get('contexts', [])
        print(f"Evaluating: {q}")

        # Baseline: hybrid
        q_emb = embed_model.encode([q])[0].tolist()
        baseline_res = retrieve_hybrid(q, q_emb, tenant_id=tenant_id, k=TOP_K)
        baseline_scores.append(precision_at_k(baseline_res, expected_contexts))

        # ---------------------------------------------------------
        # Advanced Retrieval Strategies: HyDE + Multi-Query
        # Integrated from dev-uday branch PR #11
        # ---------------------------------------------------------

        # HyDE
        prompt = [
            {"role": "system", "content": "Generate a short hypothetical document that would answer the question concisely."},
            {"role": "user", "content": q}
        ]
        hyde_doc = query_llm(prompt)
        if hyde_doc and not hyde_doc.startswith('[ERROR]'):
            hyde_emb = embed_model.encode([hyde_doc])[0].tolist()
            hyde_res = retrieve_similar(hyde_emb, tenant_id=tenant_id, entity_type=entity_type, contract_standard=contract_standard, k=TOP_K)
        else:
            hyde_res = []
        hyde_scores.append(precision_at_k(hyde_res, expected_contexts))

        # Multi-query
        paraphrase_prompt = [
            {"role": "system", "content": "Produce 3 concise paraphrases of the user's question, one per line."},
            {"role": "user", "content": q}
        ]
        resp = query_llm(paraphrase_prompt)
        paras = []
        if resp and not resp.startswith('[ERROR]'):
            for line in resp.splitlines():
                line = line.strip()
                if line:
                    paras.append(line)
        if not paras:
            paras = [q]

        combined = {}
        for p in paras:
            emb = embed_model.encode([p])[0].tolist()
            res = retrieve_similar(emb, tenant_id=tenant_id, entity_type=entity_type, contract_standard=contract_standard, k=TOP_K)
            for r in res:
                combined[r[0]] = (r[1], r[2])
        # Convert to list
        multi_res = [(cid, data[0], data[1]) for cid, data in combined.items()][:TOP_K]
        multi_scores.append(precision_at_k(multi_res, expected_contexts))

    summary = {
        'baseline': mean(baseline_scores) if baseline_scores else 0.0,
        'hyde': mean(hyde_scores) if hyde_scores else 0.0,
        'multi': mean(multi_scores) if multi_scores else 0.0
    }
    return summary


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/eval_retrievals.py <queries.json>")
        sys.exit(1)
    qpath = sys.argv[1]
    queries = load_queries(qpath)
    summary = run_evaluation(queries)

    # Print markdown table
    md = "| Method | Precision@5 | Notes |\n|---|---:|---|\n"
    md += f"| Baseline (hybrid) | {summary['baseline']:.2f} | Existing hybrid baseline |\n"
    md += f"| HyDE | {summary['hyde']:.2f} | Hypothetical doc embeddings |\n"
    md += f"| Multi-query | {summary['multi']:.2f} | Union of paraphrase retrievals |\n"

    print('\nEvaluation Summary:\n')
    print(md)

    # Save to Final_Deliverables
    os.makedirs('Final_Deliverables', exist_ok=True)
    out_path = 'Final_Deliverables/retrieval_comparison.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# Retrieval Comparison\n\n')
        f.write(md)
    print(f"Saved summary to {out_path}")


if __name__ == '__main__':
    main()

# src/core/security/protection.py
import re
from sentence_transformers import SentenceTransformer, util

_oos_model = None
_domain_centroid = None

def sanitize_query(query: str) -> str:
    dangerous_patterns = [
        r"ignore.*instruction",
        r"you are now",
        r"override.*prompt",
        r"bypass.*filter",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(f"Potentially malicious query detected: {pattern}")
    return query.strip()

def _get_oos_model_and_centroid():
    global _oos_model, _domain_centroid
    if _oos_model is None:
        _oos_model = SentenceTransformer('all-MiniLM-L6-v2')
        on_scope_queries = [
            "What are corrective actions for NCR violations?",
            "How does tunnel boring machine TBM-001 operate?",
            "What are contract liability clauses in GCC?",
            "What is the weather impact on tunnel boring operations?",
            "How do general site conditions affect project timeline?",
            "What are the reporting requirements for daily progress?",
            "Show me the latest correspondence regarding station cavern seepage."
        ]
        _domain_embeddings = _oos_model.encode(on_scope_queries)
        _domain_centroid = _domain_embeddings.mean(axis=0)
    return _oos_model, _domain_centroid

def check_query_out_of_scope(query: str, threshold: float = 0.3) -> bool:
    model, centroid = _get_oos_model_and_centroid()
    query_embedding = model.encode(query)
    similarity = util.pytorch_cos_sim(query_embedding, centroid)[0][0].item()
    return similarity < threshold

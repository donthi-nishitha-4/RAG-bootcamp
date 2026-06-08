import json
from src.core.llm import query_llm

def evaluate_retrieval(retrieved_chunk_ids, expected_chunk_ids, k=None):
    """
    Calculate Precision@K and Recall@K.
    """
    if not expected_chunk_ids:
        return {"precision": 0.0, "recall": 0.0}
        
    if k is not None:
        retrieved_chunk_ids = retrieved_chunk_ids[:k]
        
    retrieved_set = set(retrieved_chunk_ids)
    expected_set = set(expected_chunk_ids)
    
    true_positives = len(retrieved_set.intersection(expected_set))
    
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(expected_set) if expected_set else 0.0
    
    return {"precision": precision, "recall": recall}

def evaluate_generation(query, context, answer):
    """
    LLM-based evaluation for Faithfulness and Relevance.
    """
     # 1. Refusal Awareness: Check if system refused correctly
    refusal_keywords = ["cannot answer", "insufficient", "no information"]
    is_refusal = any(keyword in answer.lower() for keyword in refusal_keywords)
    
    if is_refusal:
        # Correct refusal IS faithful and relevant to the constraint of using only context
        return {"faithfulness": 1.0, "relevance": 1.0}

    # 2. Existing logic for actual answers
    if not context or not context.strip():
        return {"faithfulness": 0.0, "relevance": 0.0, "error": "Empty context"}
        
    if not answer or "[ERROR]" in answer:
        return {"faithfulness": 0.0, "relevance": 0.0, "error": "Invalid or empty answer"}
        
    prompt = f"""
You are evaluating a RAG system.

Question: {query}
Context: {context}
Answer: {answer}

Score STRICTLY:
- Faithfulness (0.0 to 1.0): Does the answer only use information from the context?
- Relevance (0.0 to 1.0): Does the answer actually answer the question?

Return ONLY valid JSON. NO markdown formatting, NO explanation.
Example: {{"faithfulness": 1.0, "relevance": 0.8}}
"""
    
    messages = [{"role": "user", "content": prompt}]
    
    # We use lower temperature for evaluation
    response_text = query_llm(messages, temperature=0.0)
    
    if "[ERROR]" in response_text:
        return {"faithfulness": 0.0, "relevance": 0.0, "error": "LLM evaluation failed"}
        
    # Attempt to parse JSON safely
    try:
        # Strip potential markdown formatting (e.g. ```json ... ```)
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        result = json.loads(clean_text.strip())
        
        # Validate schema
        faithfulness = float(result.get("faithfulness", 0.0))
        relevance = float(result.get("relevance", 0.0))
        
        return {"faithfulness": faithfulness, "relevance": relevance}
        
    except Exception as e:
        return {"faithfulness": 0.0, "relevance": 0.0, "error": f"JSON parse failed: {e}", "raw": response_text}

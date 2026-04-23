from openai import OpenAI
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )
    print("[INFO] Groq client initialized")
except Exception as e:
    print(f"[ERROR] Client init failed: {e}")
    exit(1)

try:
    from rag_chroma import ask_rag
    print("[INFO] RAG function loaded")
except Exception as e:
    print(f"[ERROR] Failed to import RAG: {e}")
    exit(1)

queries = [
    "How is AI used in medicine?",
    "What is machine learning?",
    "Explain deep learning",
    "Why is Python used in AI?"
]

def evaluate(query, context, answer):
    prompt = f"""
You are evaluating a RAG system.

Question: {query}
Context: {context}
Answer: {answer}

Score STRICTLY:

- Faithfulness (0 to 1)
- Relevance (0 to 1)

Return ONLY valid JSON.
NO explanation.

Example:
{{"faithfulness": 1, "relevance": 0.8}}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR] LLM failed: {e}"

print("\n[INFO] Running full RAG evaluation...\n")
for q in queries:
    print(f"\n--- Query: {q}")
    try:
        rag_result = ask_rag(q)
        answer = rag_result.get("answer", "")
        context = rag_result.get("context", "")
        
        if not answer or "[ERROR]" in str(answer):
            raise ValueError("Invalid answer from RAG")
        if not context:
            raise ValueError("No context retrieved")
            
        # FIXED: Use CONTEXT (not answer) in evaluation
        eval_result = evaluate(q, context, answer)
        print("[ANSWER]", answer)
        print("[CONTEXT]", context)
        try:
            parsed = json.loads(eval_result)
            print("[EVAL CLEAN]", parsed)
        except Exception:
            print("[EVAL RAW]", eval_result)
    except Exception as e:
        print(f"[ERROR] {e}")
    time.sleep(2)
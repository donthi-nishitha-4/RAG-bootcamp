import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def query_llm(messages, temperature=0.1, max_retries=2, timeout=10.0):
    """
    Query LLM with sequential fallback providers.
    Handles timeouts, retries, and sequential failover.
    """
    providers = [
        {
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
            "model": "llama-3.3-70b-versatile"
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "deepseek/deepseek-chat-v3-0324:free"
        },
        {
            "name": "cerebras",
            "base_url": "https://api.cerebras.ai/v1",
            "api_key": os.getenv("CEREBRAS_API_KEY"),
            "model": "llama3.1-70b"
        },
        {
            "name": "google",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-1.5-pro"
        }
    ]
    
    for p in providers:
        if not p.get("api_key"):
            continue
            
        for attempt in range(max_retries):
            try:
                client = OpenAI(
                    base_url=p["base_url"],
                    api_key=p["api_key"],
                    timeout=timeout
                )
                response = client.chat.completions.create(
                    model=p["model"],
                    messages=messages,
                    temperature=temperature
                )
                print(f"[INFO] Successfully used provider: {p['name']}")
                return response.choices[0].message.content
            except Exception as e:
                print(f"[WARN] {p['name']} attempt {attempt + 1} failed: {e}")
                time.sleep(1) # wait before retry
        
        # If all retries for this provider fail, move to the next provider
        print(f"[WARN] Provider {p['name']} exhausted. Failing over to next provider.")
        
    return "[ERROR] LLM unavailable"

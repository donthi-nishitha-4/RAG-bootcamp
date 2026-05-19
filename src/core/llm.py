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
            "model": "llama-3.1-8b-instant"
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "mistralai/mistral-7b-instruct:free"
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
            "model": "gemini-flash-latest"
        }
    ]
    
    for p in providers:
        if not p.get("api_key"):
            continue
            
        for attempt in range(max_retries):
            try:
                if p["name"] == "google":
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    from langchain_core.messages import HumanMessage, SystemMessage
                    
                    llm = ChatGoogleGenerativeAI(
                        model=p["model"],
                        google_api_key=p["api_key"],
                        temperature=temperature,
                        timeout=timeout
                    )
                    
                    # Convert dict messages to LangChain message objects
                    lc_messages = []
                    for m in messages:
                        if m["role"] == "system":
                            lc_messages.append(SystemMessage(content=m["content"]))
                        else:
                            lc_messages.append(HumanMessage(content=m["content"]))
                    
                    response_text = llm.invoke(lc_messages).content
                    print(f"[INFO] Successfully used provider: {p['name']}")
                    return response_text
                else:
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
                print(f"[WARN] {p['name']} attempt {attempt + 1} failed: {str(e)[:100]}...")
                time.sleep(5) # wait before retry
        
        # If all retries for this provider fail, move to the next provider
        print(f"[WARN] Provider {p['name']} exhausted. Failing over to next provider.")
        
    return "[ERROR] LLM unavailable"

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from typing import List, Any, Optional

class RobustLLM(BaseChatModel):
    """
    A robust LangChain ChatModel that uses sequential fallback providers.
    """
    temperature: float = 0.1
    
    @property
    def _llm_type(self) -> str:
        return "robust-fallback-llm"

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        # Convert LangChain messages back to dict format for query_llm
        dict_messages = []
        for m in messages:
            role = "user"
            if "system" in m.type: role = "system"
            elif "ai" in m.type: role = "assistant"
            dict_messages.append({"role": role, "content": m.content})
            
        answer = query_llm(dict_messages, temperature=self.temperature)
        
        return ChatResult(generations=[ChatGeneration(message=HumanMessage(content=answer))])

    def _get_ls_params(self, **kwargs: Any) -> Any:
        return {"model": "robust-fallback"}

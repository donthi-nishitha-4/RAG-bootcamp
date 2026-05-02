import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag_pipeline import ask_rag

class TestRAGPipeline(unittest.TestCase):
    def test_invalid_query(self):
        res = ask_rag("")
        self.assertIn("[ERROR]", res["answer"])
        
    def test_context_separation(self):
        # Even if retrieval fails, it should return context/answer keys
        res = ask_rag("test query")
        self.assertIn("context", res)
        self.assertIn("answer", res)
        # Ensure context is NOT the answer
        if res["context"] and res["answer"]:
            self.assertNotEqual(res["context"], res["answer"])

if __name__ == "__main__":
    unittest.main()

import fitz
from rag_pgvector import load_documents, init_pgvector
import sys

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"[ERROR] PDF load failed: {e}")
        sys.exit(1)

def simple_chunker(text, chunk_size=800, overlap=100):
    """Basic chunking: splits by character length with some overlap. No advanced NLP yet."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

if __name__ == "__main__":
    pdf_path = "data/GCC-2022.pdf"
    
    print(f"[INFO] 1. Extracting text from {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    
    print("[INFO] 2. Chunking text (Simple Character Splitting)")
    chunks = simple_chunker(raw_text, chunk_size=800, overlap=100)
    print(f"[INFO] Generated {len(chunks)} chunks from the PDF.")
    
    print("[INFO] 3. Preparing pgvector...")
    init_pgvector()
    
    print("[INFO] 4. Loading embeddings to pgvector with metadata...")
    # Using the required metadata fields
    tenant_id = "indian_railways"
    entity_type = "gcc_contract"
    
    success = load_documents(chunks, entity_type=entity_type, tenant_id=tenant_id)
    
    if success:
        print("\n[SUCCESS] Pipeline is now running with REAL DATA in pgvector!")
    else:
        print("\n[ERROR] Failed to ingest data.")

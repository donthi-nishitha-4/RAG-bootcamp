import fitz  # PyMuPDF
import sys

def extract_text_from_pdf(pdf_path):
    print(f"Loading {pdf_path}...")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sample_pdf = "data/GCC-2022.pdf"
    raw_text = extract_text_from_pdf(sample_pdf)
    
    print(f"Successfully extracted {len(raw_text)} characters!")
    print("\n--- Preview of first 200 characters ---")
    print(raw_text[:200].strip())
    print("---------------------------------------")

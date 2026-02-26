# scripts/extract.py

import pdfplumber

def extract_text_blocks(pdf_path, password=None):
    """
    Extract full raw text from NSDL CAS PDF.
    Supports password-protected PDFs.
    """

    print("Extracting raw text using pdfplumber...")

    full_text = []

    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)

    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""

    return "\n".join(full_text)
# scripts/extract.py

import camelot
import pandas as pd


def extract_tables(pdf_path, password=None):
    """
    Extract tables from NSDL CAS PDF using stream mode.
    Accepts optional password for encrypted PDFs.
    """

    print("Extracting tables (stream mode)...")

    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="stream",
            password=password,
            strip_text="\n"
        )
    except Exception as e:
        print(f"Camelot extraction failed: {e}")
        return pd.DataFrame()

    if not tables or tables.n == 0:
        print("No tables found by Camelot.")
        return pd.DataFrame()

    combined = pd.concat([t.df for t in tables], ignore_index=True)

    # Clean whitespace safely
    combined = combined.applymap(
        lambda x: x.strip() if isinstance(x, str) else x
    )

    combined = combined.dropna(how="all")

    return combined
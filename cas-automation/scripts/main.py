# scripts/main.py

import os
import pandas as pd

# from extract import extract_tables
from normalize import normalize
from dedupe import filter_new
from extract import extract_text_blocks
from parser import parse_transactions

PDF_PATH = "input/cas_latest.pdf"

ISIN_MAP_PATH = "config/isin_map.csv"
OUTPUT_PATH = "output/ghostfolio_import.csv"


def main():
    os.makedirs("output", exist_ok=True)

    print("Extracting tables...")
    raw = extract_tables(PDF_PATH, PASSWORD)

    print(raw.head(100))
    raw.to_csv("output/debug_raw.csv", index=False)

    print("Loading ISIN map...")
    isin_map_df = pd.read_csv(ISIN_MAP_PATH)

    print("Normalizing transactions...")
    normalized = normalize(raw, isin_map_df)

    if normalized.empty:
        print("No transactions detected.")
        return

    print("Running dedupe engine...")
    new_txns = filter_new(normalized)

    if new_txns.empty:
        print("No new transactions found.")
        return

    ghostfolio_df = new_txns.rename(columns={
        "date": "Date",
        "symbol": "Symbol",
        "quantity": "Quantity",
        "price": "Price",
        "fee": "Fee",
        "type": "Type"
    })

    ghostfolio_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Done. Saved {len(ghostfolio_df)} transactions to {OUTPUT_PATH}")

# Option 1: Hardcode (not recommended for prod)
# PASSWORD = "**hardcoded-string**"   # replace safely

# Option 2 (Recommended): Use environment variable
PASSWORD = os.getenv("CAS_PASSWORD")

if __name__ == "__main__":
#   when camelot was used
#   main()
    print("Reading CAS...")

    text = extract_text_blocks(PDF_PATH, PASSWORD)
    print(text[:5000])
    
    if not text:
        print("Failed to extract text.")
        exit(1)

    print("Parsing transactions...")
    df = parse_transactions(text)

    if df.empty:
        print("No transactions detected.")
    else:
        print(df.head())
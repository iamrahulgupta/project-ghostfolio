# scripts/resolver.py

import requests
import pandas as pd
import time
import os

ISIN_MAP_PATH = "config/isin_map.csv"

NSE_SEARCH_URL = "https://www.nseindia.com/api/search/autocomplete?q="
BSE_SEARCH_URL = "https://api.bseindia.com/BseIndiaAPI/api/Search/GetSearchData"
AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


# ------------------------
# Utility
# ------------------------

def ensure_isin_map():
    if not os.path.exists(ISIN_MAP_PATH):
        df = pd.DataFrame(columns=["ISIN", "Symbol", "AssetClass"])
        df.to_csv(ISIN_MAP_PATH, index=False)


def load_isin_map():
    ensure_isin_map()
    return pd.read_csv(ISIN_MAP_PATH)


def save_isin_map(df):
    df.to_csv(ISIN_MAP_PATH, index=False)


def classify_isin(isin: str):
    if isin.startswith("INF"):
        return "MutualFund"
    if isin.startswith("INE"):
        return "Equity"
    return "Unknown"


# ------------------------
# BSE Equity Resolver
# ------------------------

def search_bse(isin: str):
    try:
        params = {
            "text": isin,
            "type": "All"
        }

        response = requests.get(BSE_SEARCH_URL, params=params, headers=HEADERS, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        for item in data:
            if item.get("scripname"):
                return item["scripname"] + ".BO"

    except Exception:
        return None

    return None

# ------------------------
# NSE Equity Resolver
# ------------------------

def search_nse(isin: str):
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        session.get("https://www.nseindia.com", timeout=5)
        time.sleep(1)

        response = session.get(NSE_SEARCH_URL + isin, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()

        for item in data.get("symbols", []):
            if item.get("symbol"):
                return item["symbol"] + ".NS"

    except Exception:
        return None

    return None


# ------------------------
# AMFI Mutual Fund Resolver
# ------------------------

def build_amfi_cache():
    response = requests.get(AMFI_NAV_URL, timeout=10)
    lines = response.text.split("\n")

    records = []

    for line in lines:
        parts = line.split(";")
        if len(parts) >= 5:
            scheme_code = parts[0]
            scheme_name = parts[3]
            isin = parts[1]

            if isin and isin.startswith("INF"):
                records.append({
                    "ISIN": isin.strip(),
                    "SchemeName": scheme_name.strip()
                })

    return pd.DataFrame(records)


def resolve_mutual_fund(isin: str):
    try:
        df = build_amfi_cache()
        match = df[df["ISIN"] == isin]
        if not match.empty:
            scheme_name = match.iloc[0]["SchemeName"]
            return scheme_name
    except Exception:
        return None

    return None

def fetch_latest_nav(isin: str):
    try:
        response = requests.get(AMFI_NAV_URL, timeout=10)
        lines = response.text.split("\n")

        for line in lines:
            parts = line.split(";")
            if len(parts) >= 5:
                if parts[1].strip() == isin:
                    return float(parts[4])  # NAV value
    except Exception:
        return None

    return None

# ------------------------
# Main Resolver
# ------------------------

def resolve_symbol(isin: str):
    isin_map_df = load_isin_map()

    existing = isin_map_df[isin_map_df["ISIN"] == isin]
    if not existing.empty:
        return existing.iloc[0]["Symbol"]

    asset_class = classify_isin(isin)

    print(f"Resolving ISIN {isin} ({asset_class})...")

    symbol = None

    if asset_class == "Equity":
        symbol = search_nse(isin)

        if not symbol:
            print("NSE failed, trying BSE...")
            symbol = search_bse(isin)
            
    elif asset_class == "MutualFund":
        symbol = resolve_mutual_fund(isin)

    if symbol:
        new_row = pd.DataFrame([{
            "ISIN": isin,
            "Symbol": symbol,
            "AssetClass": asset_class
        }])

        isin_map_df = pd.concat([isin_map_df, new_row], ignore_index=True)
        save_isin_map(isin_map_df)

        print(f"Mapped {isin} → {symbol}")
        return symbol

    print(f"Failed to resolve ISIN {isin}")
    return None
# scripts/normalize.py

import pandas as pd
import re
from datetime import datetime
from resolver import resolve_symbol
from corporate_actions import detect_corporate_action, handle_corporate_action

DATE_PATTERN = re.compile(r"\d{2}-[A-Za-z]{3}-\d{4}")

def is_transaction_row(row):
    row_text = " ".join(str(x) for x in row if x)

    if DATE_PATTERN.search(row_text):
        if any(word in row_text.upper() for word in [
            "BUY", "SELL", "REDEMPTION", "ALLOTMENT",
            "DIVIDEND", "SIP", "PURCHASE"
        ]):
            return True

    return False


def normalize_transactions(df):
    transactions = []

    for _, row in df.iterrows():
        if is_transaction_row(row):
            transactions.append(row)

    if not transactions:
        return pd.DataFrame()

    tx_df = pd.DataFrame(transactions)
    return tx_df.reset_index(drop=True)

def parse_date(value):
    try:
        return datetime.strptime(value, "%d-%m-%Y").date()
    except:
        return None

def detect_transaction_row(row):
    row_text = " ".join(row.astype(str)).lower()

    if "buy" in row_text or "sell" in row_text:
        return True

    return False


def extract_isin(text):
    match = re.search(r"[A-Z]{2}[A-Z0-9]{10}", text)
    return match.group(0) if match else None


def normalize(raw_df: pd.DataFrame, isin_map_df: pd.DataFrame) -> pd.DataFrame:
    transactions = []

    for _, row in raw_df.iterrows():

        if not detect_transaction_row(row):
            continue

        row_text = " ".join(row.astype(str))

        action = detect_corporate_action(row_text)
        if action:
            txn = handle_corporate_action({
                "date": date,
                "symbol": symbol,
                "isin": isin,
                "quantity": quantity,
                "price": price,
                "type": txn_type,
                "fee": 0
            }, action)

            transactions.append(txn)
            continue

        isin = extract_isin(row_text)
        if not isin:
            continue

        if isin.startswith("INF"):
            from resolver import fetch_latest_nav

            latest_nav = fetch_latest_nav(isin)
            if latest_nav:
                if abs(price - latest_nav) / latest_nav > 0.15:
                    print(f"⚠ NAV deviation detected for {symbol}: CAS={price}, AMFI={latest_nav}")

        # symbol_match = isin_map_df[isin_map_df["ISIN"] == isin]
        # if symbol_match.empty:
        #    continue

        # symbol = symbol_match.iloc[0]["Symbol"]
        
        symbol = resolve_symbol(isin)
        if not symbol:
            continue

        date = None
        for cell in row:
            parsed = parse_date(str(cell))
            if parsed:
                date = parsed
                break

        if not date:
            continue

        quantity = None
        price = None
        txn_type = "BUY" if "buy" in row_text.lower() else "SELL"

        numbers = re.findall(r"\d+\.\d+|\d+", row_text)
        if len(numbers) >= 2:
            quantity = float(numbers[0])
            price = float(numbers[1])

        if not quantity or not price:
            continue

        transactions.append({
            "date": date,
            "symbol": symbol,
            "isin": isin,
            "quantity": quantity,
            "price": price,
            "type": txn_type,
            "fee": 0
        })

    return pd.DataFrame(transactions)
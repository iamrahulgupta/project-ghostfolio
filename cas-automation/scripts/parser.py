# scripts/parser.py

import re
import pandas as pd

DATE_PATTERN = r"\d{2}-[A-Za-z]{3}-\d{4}"
ISIN_PATTERN = r"IN[EA][A-Z0-9]{9}"

EXCLUDE_KEYWORDS = [
    "ENTRY LOAD",
    "EXIT LOAD",
    "EXPENSE",
    "RATIO",
    "MARKET VALUE",
    "NAV",
    "FACE VALUE",
    "MATURITY",
    "STATEMENT",
    "PERIOD",
]

ACTION_KEYWORDS = [
    "BUY",
    "SELL",
    "CREDIT",
    "DEBIT",
    "ALLOTMENT",
    "REDEMPTION",
    "DIVIDEND",
    "SIP",
    "BONUS",
    "SPLIT",
    "TRANSFER",
    "SWITCH"
]


def looks_like_quantity(line):
    # Look for decimal or integer quantity
    return re.search(r"\b\d+\.\d{2,4}\b", line) or re.search(r"\b\d+\b", line)


def is_excluded(line):
    upper = line.upper()
    return any(word in upper for word in EXCLUDE_KEYWORDS)


def is_transaction_line(line):
    if not re.search(DATE_PATTERN, line):
        return False

    if is_excluded(line):
        return False

    if not looks_like_quantity(line):
        return False

    upper = line.upper()

    if any(keyword in upper for keyword in ACTION_KEYWORDS):
        return True

    # Sometimes CAS uses Cr/Dr
    if " CR" in upper or " DR" in upper:
        return True

    return False


def parse_transactions(text):

    lines = text.split("\n")
    transactions = []

    current_isin = None
    current_security = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Detect security header
        isin_match = re.search(ISIN_PATTERN, line)
        if isin_match and not is_transaction_line(line):
            current_isin = isin_match.group()
            current_security = line
            continue

        # Detect real transaction
        if is_transaction_line(line):
            transactions.append({
                "security": current_security,
                "isin": current_isin,
                "raw_line": line
            })

    return pd.DataFrame(transactions)
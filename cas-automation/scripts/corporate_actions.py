# scripts/corporate_actions.py

import re


def detect_corporate_action(row_text: str):
    text = row_text.lower()

    if "bonus" in text:
        return "BONUS"

    if "split" in text:
        return "SPLIT"

    if "dividend" in text:
        return "DIVIDEND"

    return None


def handle_corporate_action(txn, action_type):
    if action_type == "DIVIDEND":
        txn["type"] = "DIVIDEND"
        txn["quantity"] = 0
        txn["price"] = 0

    elif action_type == "BONUS":
        txn["type"] = "BUY"
        txn["price"] = 0  # bonus shares cost zero

    elif action_type == "SPLIT":
        # split handled implicitly via quantity in CAS
        txn["type"] = "SPLIT"

    return txn
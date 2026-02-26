# scripts/dedupe.py

import sqlite3
import hashlib
import os

DB_PATH = "state/processed_hashes.db"


def init_db():
    os.makedirs("state", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            hash TEXT PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()


def generate_hash(txn):
    key = f"{txn['date']}-{txn['symbol']}-{txn['quantity']}-{txn['price']}-{txn['type']}"
    return hashlib.sha256(key.encode()).hexdigest()


def filter_new(df):
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_rows = []

    for _, row in df.iterrows():
        txn_hash = generate_hash(row)

        cursor.execute("SELECT 1 FROM transactions WHERE hash = ?", (txn_hash,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("INSERT INTO transactions (hash) VALUES (?)", (txn_hash,))
            new_rows.append(row)

    conn.commit()
    conn.close()

    return df.iloc[[df.index.get_loc(r.name) for r in new_rows]] if new_rows else df.iloc[0:0]
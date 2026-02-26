
## camelot-based flow
NSDL CAS PDF
     ↓
Structured Table Extraction (Camelot)
     ↓
Section Classifier (Equity / MF / CA / Dividend)
     ↓
Transaction Normalizer
     ↓
ISIN → Symbol Resolver
     ↓
Deduplication Engine
     ↓
Ghostfolio-Ready CSV

## pdf***-based flow

ISIN
  ↓
Asset classifier
  ↓
NSE lookup → if fails → BSE lookup
  ↓
Cache locally

Transactions
  ↓
Detect Corporate Actions
  ↓
Normalize
  ↓
NAV validation (MF only)
  ↓
Dedupe
  ↓
Ghostfolio CSV

## DB Architecture Summary

User → Ghostfolio API
              ↓
        PostgreSQL (persistent data)
              ↓
        Redis (cache / speed layer)

## Note

# Place tokens in .env file

openssl rand -base64 32

Run it twice and paste values into:

ACCESS_TOKEN_SALT=
JWT_SECRET_KEY=
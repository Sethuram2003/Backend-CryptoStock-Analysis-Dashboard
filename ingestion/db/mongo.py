# ingestion/db/mongo.py
import os
from typing import Optional
from pymongo import MongoClient

# Keep a small cache so repeated calls reuse the same client
_CLIENTS = {}

def get_client(kind: Optional[str] = None) -> MongoClient:
    """
    kind can be: 'crypto', 'stocks', or None.
    Order of precedence:
      crypto  -> MONGODB_CRYPTO_URI -> MONGODB_URI
      stocks  -> MONGODB_STOCK_URI  -> MONGODB_URI
      None    -> MONGODB_URI
    """
    if kind == "crypto":
        uri = os.getenv("MONGODB_CRYPTO_URI") or os.getenv("MONGODB_URI")
    elif kind == "stocks":
        uri = os.getenv("MONGODB_STOCK_URI") or os.getenv("MONGODB_URI")
    else:
        uri = os.getenv("MONGODB_URI")

    if not uri:
        raise RuntimeError(
            "No MongoDB URI set. Set MONGODB_URI or "
            "MONGODB_CRYPTO_URI / MONGODB_STOCK_URI."
        )

    key = (kind or "default", uri)
    if key not in _CLIENTS:
        _CLIENTS[key] = MongoClient(uri, serverSelectionTimeoutMS=10000)
    return _CLIENTS[key]

def get_collection(kind: str, collection_name: Optional[str] = None):
    """
    Returns a collection handle from database MONGODB_DATABASE (default 'Raw_data').
    If collection_name is not passed, it falls back to:
      crypto -> MONGODB_CRYPTO_COL (default 'Cryoto')
      stocks -> MONGODB_STOCK_COL  (default 'Stock_Market')
    """
    db_name = os.getenv("MONGODB_DATABASE", "Raw_data")
    if collection_name is None:
        if kind == "crypto":
            collection_name = os.getenv("MONGODB_CRYPTO_COL", "Crypto")
        elif kind == "stocks":
            collection_name = os.getenv("MONGODB_STOCK_COL", "Stock_Market")
        else:
            raise ValueError("kind must be 'crypto' or 'stocks' when collection_name is not provided")

    client = get_client(kind)
    return client[db_name][collection_name]

def ping(kind: Optional[str] = None) -> bool:
    """
    Pings the MongoDB deployment to verify connectivity.
    """
    client = get_client(kind)
    client.admin.command("ping")
    return True

if __name__ == "__main__":
    # Allow quick CLI testing:
    import argparse
    parser = argparse.ArgumentParser(description="Ping MongoDB")
    parser.add_argument("--kind", choices=["crypto", "stocks"], default=None)
    args = parser.parse_args()
    ok = ping(args.kind)
    print({"ok": ok, "kind": args.kind})

# ingestion/run_ingestion.py
import argparse
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

# ✅ Import and include module routers
from ingestion.crypto.coingeeko import router as crypto_router, fetch_crypto_data
from ingestion.stocks.ytfinance import router as stocks_router, fetch_stock_data

DATA_ROOT = Path("ingestion/data")
(DATA_ROOT / "crypto").mkdir(parents=True, exist_ok=True)
(DATA_ROOT / "stocks").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Ingestion Service", version="1.1.0")

# Health stays here
@app.get("/health")
def health():
    return {"status": "ok"}

# Include routers defined in modules
app.include_router(crypto_router)
app.include_router(stocks_router)

# Convenience endpoint to run both (kept in the main app)
class BothResult(BaseModel):
    crypto: dict
    stocks: dict

@app.post("/ingest/all", response_model=BothResult)
def ingest_all():
    c = fetch_crypto_data(output_dir=str(DATA_ROOT / "crypto"))
    s = fetch_stock_data(output_dir=str(DATA_ROOT / "stocks"))
    return {"crypto": c, "stocks": s}

# ---- CLI so you can cron it without HTTP
def _cli():
    parser = argparse.ArgumentParser(description="Run ingestion once or start API.")
    parser.add_argument("--once", action="store_true", help="Run both crypto and stocks once and exit.")
    parser.add_argument("--only", choices=["crypto", "stocks"], help="Limit to one source when using --once.")
    parser.add_argument("--crypto-ids", type=str, help="Comma-separated CoinGecko IDs for --once.")
    parser.add_argument("--tickers", type=str, help="Comma-separated tickers for --once.")
    parser.add_argument("--uvicorn", action="store_true", help="Start FastAPI server with uvicorn.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.once:
        ids = [s.strip() for s in (args.crypto_ids or "").split(",")] if args.crypto_ids else None
        tks = [s.strip().upper() for s in (args.tickers or "").split(",")] if args.tickers else None

        if args.only == "crypto":
            res = fetch_crypto_data(crypto_ids=ids, output_dir=str(DATA_ROOT / "crypto"))
            print(res)
        elif args.only == "stocks":
            res = fetch_stock_data(tickers=tks, output_dir=str(DATA_ROOT / "stocks"))
            print(res)
        else:
            res_c = fetch_crypto_data(crypto_ids=ids, output_dir=str(DATA_ROOT / "crypto"))
            res_s = fetch_stock_data(tickers=tks, output_dir=str(DATA_ROOT / "stocks"))
            print({"crypto": res_c, "stocks": res_s})
        return

    if args.uvicorn:
        import uvicorn
        uvicorn.run("ingestion.run_ingestion:app", host=args.host, port=args.port, reload=False)
        return

    parser.print_help()

if __name__ == "__main__":
    _cli()

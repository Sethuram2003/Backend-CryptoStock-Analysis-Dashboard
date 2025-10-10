
from pathlib import Path

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



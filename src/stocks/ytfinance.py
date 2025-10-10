# ingestion/stocks/ytfinance.py
import yfinance as yf
import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

# --- FastAPI router bits
from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.schemas import IngestResult

DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
DATA_DIR = Path("ingestion/data/stocks")

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_stock_data(
    tickers: Optional[List[str]] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    tickers = tickers or DEFAULT_TICKERS
    outdir = Path(output_dir or DATA_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

    all_stock_data: Dict[str, Any] = {}

    for tkr in tickers:
        stock = yf.Ticker(tkr)
        info = stock.info  # may be delayed data
        hist = stock.history(period="1d", interval="1m")

        stock_data = {
            "ticker": tkr,
            "company_name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice", "N/A"),
            "previous_close": info.get("previousClose", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "volume": info.get("volume", "N/A"),
            "timestamp": _now_iso_utc(),
            "historical_data": []
        }

        if not hist.empty:
            hist = hist.reset_index()
            for _, row in hist.iterrows():
                dt = (
                    row['Datetime'] if 'Datetime' in row
                    else row['Date'] if 'Date' in row
                    else row.get('index')
                )
                if isinstance(dt, pd.Timestamp):
                    dt_iso = dt.isoformat()
                else:
                    dt_iso = str(dt)

                stock_data["historical_data"].append({
                    "datetime": dt_iso,
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })

        all_stock_data[tkr] = stock_data

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = outdir / f"stock_data_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(all_stock_data, f, indent=2, ensure_ascii=False)

    return {"path": str(path), "count": len(all_stock_data)}

def fetch_single_stock(
    ticker: str,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    outdir = Path(output_dir or DATA_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

    stock = yf.Ticker(ticker)
    info = stock.info

    payload = {
        "ticker": ticker,
        "company_name": info.get("longName", "N/A"),
        "current_price": info.get("currentPrice", "N/A"),
        "day_high": info.get("dayHigh", "N/A"),
        "day_low": info.get("dayLow", "N/A"),
        "volume": info.get("volume", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "timestamp": _now_iso_utc()
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = outdir / f"stock_{ticker}_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return {"path": str(path), "ticker": ticker}

# ---------- FastAPI Router ----------


router = APIRouter(prefix="/ingest/stocks", tags=["stocks"])

@router.post("", response_model=IngestResult)
def ingest_stocks(tickers: Optional[str] = Query(None, description="Comma-separated tickers"),
                  output_dir: Optional[str] = None):
    tickers_list: Optional[List[str]] = None
    if tickers:
        tickers_list = [s.strip().upper() for s in tickers.split(",") if s.strip()]
    return fetch_stock_data(tickers=tickers_list, output_dir=output_dir or str(DATA_DIR))

@router.post("/single", response_model=IngestResult)
def ingest_stock_single(ticker: str,
                        output_dir: Optional[str] = None):
    return fetch_single_stock(ticker=ticker.upper(), output_dir=output_dir or str(DATA_DIR))

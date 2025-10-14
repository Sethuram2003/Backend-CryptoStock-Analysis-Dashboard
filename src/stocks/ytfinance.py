# ingestion/stocks/ytfinance.py
import yfinance as yf
import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

# --- FastAPI router bits
from fastapi import APIRouter, Query
from src.utils.mongo import mongo

DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_stock_data(
    tickers: Optional[List[str]] = None
) -> Dict[str, Any]:
    tickers = tickers or DEFAULT_TICKERS
    

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
    mongo.connect()
    mongo.insert(collection_name="Stock_Market", data={"fetched_at": _now_iso_utc(), "data": all_stock_data})

    return {"MongoDB Inserted": "Stock_Market", "count": len(all_stock_data)}
    #return all_stock_data

def fetch_single_stock(
    ticker: str
) -> Dict[str, Any]:


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

    mongo.connect()
    mongo.insert(collection_name="Stock_Market", data={"fetched_at": _now_iso_utc(), "data": payload})

    return {"MongoDB Inserted": "Stock_Market", "count": len(payload)}
    #return payload


router = APIRouter(prefix="/ingest/stocks", tags=["stocks"])

@router.post("")
def ingest_stocks(tickers: Optional[str] = Query(None, description="Comma-separated tickers")):
    tickers_list: Optional[List[str]] = None
    if tickers:
        tickers_list = [s.strip().upper() for s in tickers.split(",") if s.strip()]
    return fetch_stock_data(tickers=tickers_list)

@router.post("/single")
def ingest_stock_single(ticker: str):
    return fetch_single_stock(ticker=ticker.upper())

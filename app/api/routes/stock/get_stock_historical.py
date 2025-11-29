from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from app.core.StockData import fetch_stock_history
import pandas as pd

stock_historical_router = APIRouter(tags=["Stock"])

def convert_keys(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            # convert key to string (handles Timestamp, datetime, etc)
            key = str(k)  
            new_dict[key] = convert_keys(v)
        return new_dict
    elif isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    else:
        # convert Timestamps in values too
        if isinstance(obj, (pd.Timestamp)):
            return str(obj)
        return obj


@stock_historical_router.get("/get-stock-historical")
def get_stock_historical(ticker: str = "AAPL", days: int = 7):

    payload = fetch_stock_history(ticker=ticker, days=days)

    clean_payload = convert_keys(payload)

    return JSONResponse({'message': clean_payload})

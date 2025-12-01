from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

from app.core.mongodb import MongoDB


stock_data_router = APIRouter(tags=["Stock"])

app = FastAPI()

@stock_data_router.get("/get-stock-data")
def get_stock_data(ticker: str = "AAPL"):

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    try:
        mongo.connect()
        # Fetch the latest data blob from the database
        latest_doc = mongo.get_latest(collection_name="Stock_Market")
        
        if not latest_doc:
             raise HTTPException(status_code=404, detail="No stock data available.")

        # The structure in DB is {"data": {"fetched_at": ..., "data": {"AAPL": ...}}}
        full_data = latest_doc.get("data", {})
        market_data = full_data.get("data", {})
        
        if ticker not in market_data:
             raise HTTPException(status_code=404, detail=f"Data for '{ticker}' not found in cache.")

        # Construct response similar to original
        response_payload = {
            "fetched_at": full_data.get("fetched_at"),
            "data": {
                ticker: market_data[ticker]
            }
        }

        return JSONResponse({'message': response_payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

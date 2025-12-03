from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os

from app.core.StockData import fetch_stock_data
from app.core.mongodb import MongoDB


stock_data_router = APIRouter(tags=["Stock"])

app = FastAPI()

@stock_data_router.get("/get-stock-data")
def get_stock_data(ticker: str = "AAPL"):

    payload = fetch_stock_data([ticker])

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    mongo.connect()
    mongo.insert(collection_name="Stock_Market", data={"data": payload})

    return JSONResponse({'message': payload})
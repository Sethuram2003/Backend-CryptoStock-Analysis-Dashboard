from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.lang_graph.builder import build_graph
from app.core.mongodb import MongoDB

stock_sentiment_router = APIRouter(tags=["Stock"])

app = FastAPI()

executor = ThreadPoolExecutor(max_workers=5)

def process_stock_sentiment(ticker: str, days: int):
    agent = build_graph()
    response = agent.invoke({
        "coin_name": ticker,   
        "days": days
    })

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    mongo.connect()
    mongo.insert(
        collection_name="Stock_Market_News",
        data={
            "data": response["final_report"].model_dump(mode="json"),
            "ticker": ticker,
            "days": days
        }
    )

    return response["final_report"].model_dump(mode="json")


@stock_sentiment_router.put("/put-stock-sentiment")
async def get_stock_sentiment(ticker: str = "AAPL", days: int = 7):
    loop = asyncio.get_event_loop()

    result = await loop.run_in_executor(
        executor,
        process_stock_sentiment,
        ticker,
        days
    )

    return JSONResponse({"response": result})

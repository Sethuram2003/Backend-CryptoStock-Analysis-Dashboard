from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.lang_graph.builder import build_graph
from app.core.mongodb import MongoDB

crypto_sentiment_router = APIRouter(tags=["Crypto"])

app = FastAPI()

executor = ThreadPoolExecutor(max_workers=5)

def process_sentiment(coin_id: str, days: int):
    agent = build_graph()
    response = agent.invoke({
        "coin_name": coin_id,
        "days": days
    })

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    mongo.connect()
    mongo.insert(
        collection_name="Crypto_News",
        data={
            "data": response["final_report"].model_dump(mode="json"),
            "coin_name": coin_id,
            "days": days
        },
    )

    return response["final_report"].model_dump(mode="json")


@crypto_sentiment_router.put("/put-crypto-sentiment")
async def get_crypto_sentiment(coin_id: str = "bitcoin", days: int = 7):
    loop = asyncio.get_event_loop()

    result = await loop.run_in_executor(
        executor,
        process_sentiment,
        coin_id,
        days
    )

    return JSONResponse({"response": result})

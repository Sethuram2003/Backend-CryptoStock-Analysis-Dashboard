from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os

from app.core.lang_graph.builder import build_graph
from app.core.mongodb import MongoDB

stock_sentiment_router = APIRouter(tags=["Stock"])

app = FastAPI()
@stock_sentiment_router.put("/put-stock-sentiment")
def get_stock_sentiment(ticker: str = "AAPL", days: int = 7):

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
    mongo.insert(collection_name="Stock_Market_News", data={"data": response["final_report"].model_dump(mode="json"),"ticker":ticker, "days":days})
    
    
    return JSONResponse({"response": response["final_report"].model_dump(mode="json")})

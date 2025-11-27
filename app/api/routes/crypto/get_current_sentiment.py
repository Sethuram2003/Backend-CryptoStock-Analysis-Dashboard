from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from app.core.lang_graph.builder import build_graph

 
crypto_sentiment_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_sentiment_router.put("/put-crypto-sentiment")
def get_crypto_sentiment(coin_id: str = "bitcoin", days: int = 7):

    agent = build_graph()
    response = agent.invoke({
                    "coin_name": coin_id,
                    "days": days
                })
    
    return JSONResponse({"response": response["final_report"].model_dump(mode="json")})

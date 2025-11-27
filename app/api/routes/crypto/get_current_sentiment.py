from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from app.core.data_loader import fetch_crypto_history

 
crypto_sentiment_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_sentiment_router.get("/get-crypto-sentiment")
def get_crypto_sentiment(coin_id: str = "bitcoin", days: int = 7):

    payload = fetch_crypto_history(coin_id=coin_id, days=days)
    
    return JSONResponse({'message': payload})
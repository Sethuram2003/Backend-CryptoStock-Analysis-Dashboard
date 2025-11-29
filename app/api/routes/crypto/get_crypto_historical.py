from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from app.core.CryptoData import fetch_crypto_history

 
crypto_historical_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_historical_router.get("/get-crypto-historical")
def get_crypto_historical(coin_id: str = "bitcoin", days: int = 7):

    payload = fetch_crypto_history(coin_id=coin_id, days=days)
    
    return JSONResponse({'message': payload})
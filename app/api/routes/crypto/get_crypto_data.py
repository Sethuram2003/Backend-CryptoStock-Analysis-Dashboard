from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
import os

from app.core.CryptoData import fetch_crypto_data
from app.core.mongodb import MongoDB


crypto_data_router = APIRouter(tags=["Crypto"])

app = FastAPI()

@crypto_data_router.get("/get-crypto-data")
def get_crypto_data(coin_id: str = "bitcoin"):

    payload = fetch_crypto_data([coin_id])

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    mongo.connect()
    mongo.insert(collection_name="Crypto", data={"data": payload})

    return JSONResponse({'message': payload})
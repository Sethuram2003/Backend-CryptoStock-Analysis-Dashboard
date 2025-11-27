from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from app.core.data_loader import fetch_crypto_data

 
crypto_data_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_data_router.get("/get-crypto-data")
def get_crypto_data():

    payload = fetch_crypto_data()

    return JSONResponse({'message': payload})
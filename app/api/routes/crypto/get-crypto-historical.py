from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

 
crypto_historical_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_historical_router.get("/get-crypto-historical")
def get_crypto_historical():

    
    return JSONResponse({'message': "Crypto"}, status_code=200)
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

 
crypto_data_router = APIRouter(tags=["Crypto"])

app = FastAPI()
@crypto_data_router.get("/get-crypto-data")
def get_crypto_data():

    
    return JSONResponse({'message': "Crypto data endpoint"}, status_code=200)
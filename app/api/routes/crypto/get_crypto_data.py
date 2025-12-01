from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

from app.core.mongodb import MongoDB


crypto_data_router = APIRouter(tags=["Crypto"])

app = FastAPI()

@crypto_data_router.get("/get-crypto-data")
def get_crypto_data(coin_id: str = "bitcoin"):

    mongo = MongoDB(
        uri=os.getenv("MONGODB_URL"),
        db_name=os.getenv("MONGODB_DATABASE")
    )

    try:
        mongo.connect()
        # Fetch the latest data blob from the database
        latest_doc = mongo.get_latest(collection_name="Crypto")
        
        if not latest_doc:
             raise HTTPException(status_code=404, detail="No crypto data available.")

        # The structure in DB is {"data": {"fetched_at": ..., "data": {"bitcoin": ...}}}
        # We need to extract the specific coin data if requested.
        
        full_data = latest_doc.get("data", {})
        market_data = full_data.get("data", {})
        
        if coin_id not in market_data:
             # If specific coin not found, we return what we have or 404?
             # The original behavior fetched specific data. 
             # Now we only have cached defaults.
             raise HTTPException(status_code=404, detail=f"Data for '{coin_id}' not found in cache.")

        # Construct response similar to original
        response_payload = {
            "fetched_at": full_data.get("fetched_at"),
            "data": {
                coin_id: market_data[coin_id]
            }
        }

        return JSONResponse({'message': response_payload})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

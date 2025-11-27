from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routes.crypto.get_current_sentiment import crypto_sentiment_router
from app.api.routes.crypto.get_crypto_data import crypto_data_router
from app.api.routes.crypto.get_crypto_historical import crypto_historical_router
from app.api.routes.health_check import health_check_router

load_dotenv()

app = FastAPI(title="Crypto and Stock Analysis Service", version="1.0.0")

app.include_router(health_check_router)

app.include_router(crypto_data_router)
app.include_router(crypto_sentiment_router)
app.include_router(crypto_historical_router)

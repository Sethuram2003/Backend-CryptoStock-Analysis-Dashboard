from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.crypto.get_current_sentiment import crypto_sentiment_router
from app.api.routes.crypto.get_crypto_data import crypto_data_router
from app.api.routes.crypto.get_crypto_historical import crypto_historical_router

from app.api.routes.stock.get_stock_data import stock_data_router
from app.api.routes.stock.get_stock_historical import stock_historical_router
from app.api.routes.stock.get_stock_sentiment import stock_sentiment_router

from app.api.routes.chat import chat_router

from app.api.routes.health_check import health_check_router

load_dotenv()

app = FastAPI(title="Crypto and Stock Analysis Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],     
    allow_headers=["*"],      
)

app.include_router(health_check_router)

app.include_router(crypto_data_router)
app.include_router(crypto_sentiment_router)
app.include_router(crypto_historical_router)

app.include_router(stock_data_router)
app.include_router(stock_historical_router)
app.include_router(stock_sentiment_router)

app.include_router(chat_router)

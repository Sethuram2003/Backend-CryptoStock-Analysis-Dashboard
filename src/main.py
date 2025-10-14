from fastapi import FastAPI

from src.crypto.coingeeko import router as crypto_router
from src.stocks.ytfinance import router as stocks_router


app = FastAPI(title="Ingestion Service", version="1.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(crypto_router)
app.include_router(stocks_router)





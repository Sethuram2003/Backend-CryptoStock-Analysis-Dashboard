import json
import os
import time
import sys
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import yfinance as yf

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# --- Configuration ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = "stock_market_data"
DEFAULT_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_stock_data(tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetches current stock data from yfinance (logic moved from app/core/StockData.py)
    """
    tickers = tickers or DEFAULT_TICKERS
    all_stock_data = {}

    print(f"Fetching data for: {tickers}")
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.fast_info 

            stock_info = {
                "symbol": symbol,
                "current_price": info.get("last_price", "N/A"),
                "previous_close": info.get("previous_close", "N/A"),
                "open_price": info.get("open", "N/A"),
                "day_high": info.get("day_high", "N/A"),
                "day_low": info.get("day_low", "N/A"),
                "market_cap": info.get("market_cap", "N/A"),
                "volume": info.get("volume", "N/A"),
                "exchange": info.get("exchange", "N/A"),
                "currency": info.get("currency", "USD"),
                "timestamp": _now_iso_utc(),
            }
            all_stock_data[symbol] = stock_info
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    return {"fetched_at": _now_iso_utc(), "data": all_stock_data}

def run_producer():
    """
    Initializes Kafka Producer and publishes fetched data.
    """
    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        return

    print("Starting Stock Producer Loop...")
    while True:
        data = fetch_stock_data()
        
        if data and data.get("data"):
            try:
                producer.send(TOPIC_NAME, value=data)
                producer.flush()
                print(f"Published data to topic '{TOPIC_NAME}' at {data['fetched_at']}")
            except Exception as e:
                print(f"Failed to send data to Kafka: {e}")
        
        # Fetch interval (e.g., every 60 seconds)
        time.sleep(60)

if __name__ == "__main__":
    run_producer()

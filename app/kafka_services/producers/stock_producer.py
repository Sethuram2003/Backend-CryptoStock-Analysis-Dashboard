import json
import os
import time
import sys
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import yfinance as yf
import logging

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# --- Configuration ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = "stock_market_data"
DEFAULT_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]

logging.basicConfig(level=logging.INFO)

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_stock_data(tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetches current stock data from yfinance (logic moved from app/core/StockData.py)
    """
    logging.info("Starting to fetch stock data")
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
            logging.error(f"Error fetching data for {symbol}: {e}", exc_info=True)

    logging.info("Finished fetching stock data")
    return {"fetched_at": _now_iso_utc(), "data": all_stock_data}

def run_producer():
    """
    Initializes Kafka Producer and publishes fetched data.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Stock Data Producer")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    time.sleep(15)

    logging.info(f"Connecting to Kafka at {KAFKA_BROKER}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except KafkaError as e:
        logging.error(f"Failed to connect to Kafka: {e}", exc_info=True)
        raise

    logging.info(f"Starting Stock Producer (Run Once: {args.run_once})...")
    while True:
        data = fetch_stock_data()
        
        if data and data.get("data"):
            try:
                producer.send(TOPIC_NAME, value=data)
                producer.flush()
                logging.info(f"Published data to topic '{TOPIC_NAME}' at {data['fetched_at']}")
            except Exception as e:
                logging.error(f"Failed to send data to Kafka: {e}", exc_info=True)
                raise
        
        if args.run_once:
            break

        # Fetch interval (e.g., every 60 seconds)
        time.sleep(60)

if __name__ == "__main__":
    run_producer()

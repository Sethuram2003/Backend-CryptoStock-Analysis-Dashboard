import json
import os
import time
import sys
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from confluent_kafka import Producer
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

def _get_last_price_from_history(stock: yf.Ticker) -> Optional[float]:
    try:
        h = stock.history(period="5d")
        if h is not None and not h.empty:
            return float(h["Close"].dropna().iloc[-1])
    except Exception:
        return None
    return None

def fetch_stock_data(tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    tickers = tickers or DEFAULT_TICKERS
    all_stock_data: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)

            try:
                info = getattr(stock, "fast_info", {}) or {}
            except Exception:
                info = {}

            last_price = info.get("lastPrice")
            prev_close = info.get("previousClose")
            open_price = info.get("open")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")
            market_cap = info.get("marketCap")
            volume = info.get("lastVolume")
            exchange = info.get("exchange")
            currency = info.get("currency")

            if last_price in (None, "N/A"):
                last_price = _get_last_price_from_history(stock)
                if last_price is None:
                    try:
                        slow_info = stock.info or {}
                        last_price = slow_info.get("regularMarketPrice", "N/A")
                        prev_close = prev_close or slow_info.get("previousClose")
                        market_cap = market_cap or slow_info.get("marketCap")
                        currency = currency or slow_info.get("currency")
                        exchange = exchange or slow_info.get("exchange")
                    except Exception:
                        last_price = last_price if last_price is not None else "N/A"

            stock_info = {
                "symbol": symbol,
                "current_price": last_price if last_price is not None else "N/A",
                "previous_close": prev_close if prev_close is not None else "N/A",
                "open_price": open_price if open_price is not None else "N/A",
                "day_high": day_high if day_high is not None else "N/A",
                "day_low": day_low if day_low is not None else "N/A",
                "market_cap": market_cap if market_cap is not None else "N/A",
                "volume": volume if volume is not None else "N/A",
                "exchange": exchange if exchange is not None else "N/A",
                "currency": currency if currency is not None else "USD",
                "timestamp": _now_iso_utc(),
            }

            all_stock_data[symbol] = stock_info

        except Exception as e:
            logger.exception("Error fetching data for %s", symbol)
            errors[symbol] = str(e)
            all_stock_data[symbol] = {
                "symbol": symbol,
                "error": str(e),
                "timestamp": _now_iso_utc(),
            }

    return {"fetched_at": _now_iso_utc(), "data": all_stock_data, "errors": errors}

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
    producer_conf = {'bootstrap.servers': KAFKA_BROKER}
    producer = Producer(producer_conf)

    logging.info(f"Starting Stock Producer (Run Once: {args.run_once})...")
    while True:
        data = fetch_stock_data()
        
        if data and data.get("data"):
            try:
                producer.produce(TOPIC_NAME, value=json.dumps(data).encode('utf-8'))
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

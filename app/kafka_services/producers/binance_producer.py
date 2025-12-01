import json
import os
import time
import sys
import argparse
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
from binance.client import Client

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# --- Configuration ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = "crypto_market_data"

# Mapping: Internal Coin ID -> Binance Symbol
# We format the output to match CoinGecko so the existing consumer works.
SYMBOL_MAP = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "ADAUSDT": "cardano",
    "SOLUSDT": "solana",
    "DOGEUSDT": "dogecoin"
}

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_binance_data() -> Dict[str, Any]:
    """
    Fetches current crypto data from Binance Spot API.
    """
    client = Client() # Public endpoints don't need keys
    all_crypto_data = {}

    try:
        print(f"Fetching data from Binance for: {list(SYMBOL_MAP.keys())}")
        # Get 24hr ticker price change statistics
        tickers = client.get_ticker()
        
        # Convert list to dict for O(1) access
        ticker_map = {t['symbol']: t for t in tickers}

        for symbol, internal_id in SYMBOL_MAP.items():
            if symbol not in ticker_map:
                continue
            
            data = ticker_map[symbol]
            
            # Normalize to CoinGecko-like Schema used in crypto_producer.py
            crypto_info = {
                "id": internal_id,
                "name": internal_id.capitalize(), # Approximate name
                "symbol": symbol.replace("USDT", ""),
                "current_price_usd": float(data.get("lastPrice", 0)),
                "current_price_eur": "N/A", # Binance basic ticker is pair-specific
                "market_cap_usd": "N/A",    # Ticker endpoint doesn't give market cap
                "market_cap_eur": "N/A",
                "24h_volume_usd": float(data.get("quoteVolume", 0)), # Quote volume is in USDT
                "24h_volume_eur": "N/A",
                "24h_change_percentage": float(data.get("priceChangePercent", 0)),
                "market_cap_rank": "N/A",
                "circulating_supply": "N/A",
                "total_supply": "N/A",
                "max_supply": "N/A",
                "timestamp": _now_iso_utc(),
                "last_updated_epoch": data.get("closeTime")
            }
            all_crypto_data[internal_id] = crypto_info

        return {"fetched_at": _now_iso_utc(), "data": all_crypto_data}

    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return {}

def run_producer():
    """
    Initializes Kafka Producer and publishes fetched data.
    """
    parser = argparse.ArgumentParser(description="Binance Data Producer")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        return

    print(f"Starting Binance Producer (Run Once: {args.run_once})...")
    while True:
        data = fetch_binance_data()
        
        if data:
            try:
                producer.send(TOPIC_NAME, value=data)
                producer.flush()
                print(f"Published Binance data to topic '{TOPIC_NAME}' at {data['fetched_at']}")
            except Exception as e:
                print(f"Failed to send data to Kafka: {e}")
        
        if args.run_once:
            break
        
        time.sleep(60)

if __name__ == "__main__":
    run_producer()

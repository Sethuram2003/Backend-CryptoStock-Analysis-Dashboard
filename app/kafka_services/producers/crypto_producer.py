import json
import os
import time
import sys
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
from pycoingecko import CoinGeckoAPI

# Add the project root to the python path so we can import from app if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# --- Configuration ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = "crypto_market_data"
DEFAULT_IDS = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']

def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def fetch_crypto_data(crypto_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Fetches current crypto data from CoinGecko (logic moved from app/core/CryptoData.py)
    """
    crypto_ids = crypto_ids or DEFAULT_IDS
    cg = CoinGeckoAPI()
    all_crypto_data = {}

    try:
        print(f"Fetching data for: {crypto_ids}")
        price_data = cg.get_price(
            ids=",".join(crypto_ids),
            vs_currencies="usd,eur",
            include_market_cap=True,
            include_24hr_vol=True,
            include_24hr_change=True,
            include_last_updated_at=True
        )

        for cid in crypto_ids:
            if cid not in price_data:
                continue
            
            # Note: get_coin_by_id is rate-limited heavily. For a production producer, 
            # we might want to optimize this or use a paid key. 
            # For now, we keep the logic identical to the original file.
            try:
                coin = cg.get_coin_by_id(cid)
            except Exception as e:
                print(f"Error fetching details for {cid}: {e}")
                coin = {}

            pd = price_data[cid]

            crypto_info = {
                "id": cid,
                "name": coin.get("name", "N/A"),
                "symbol": coin.get("symbol", "").upper(),
                "current_price_usd": pd.get("usd", "N/A"),
                "current_price_eur": pd.get("eur", "N/A"),
                "market_cap_usd": pd.get("usd_market_cap", "N/A"),
                "market_cap_eur": pd.get("eur_market_cap", "N/A"),
                "24h_volume_usd": pd.get("usd_24h_vol", "N/A"),
                "24h_volume_eur": pd.get("eur_24h_vol", "N/A"),
                "24h_change_percentage": pd.get("usd_24h_change", "N/A"),
                "market_cap_rank": coin.get("market_cap_rank", "N/A"),
                "circulating_supply": coin.get("market_data", {}).get("circulating_supply", "N/A"),
                "total_supply": coin.get("market_data", {}).get("total_supply", "N/A"),
                "max_supply": coin.get("market_data", {}).get("max_supply", "N/A"),
                "timestamp": _now_iso_utc(),
                "last_updated_epoch": pd.get("last_updated_at", "N/A")
            }
            all_crypto_data[cid] = crypto_info
            
            # Sleep briefly to respect rate limits if running in a tight loop
            time.sleep(1) 

        return {"fetched_at": _now_iso_utc(), "data": all_crypto_data}

    except Exception as e:
        print(f"Error fetching crypto data: {e}")
        return {}

def run_producer():
    """
    Initializes Kafka Producer and publishes fetched data.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Crypto Data Producer")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    time.sleep(15)

    print(f"Connecting to Kafka at {KAFKA_BROKER}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        return

    print(f"Starting Crypto Producer (Run Once: {args.run_once})...")
    
    while True:
        data = fetch_crypto_data()
        
        if data:
            try:
                # We publish the whole payload as a single message
                producer.send(TOPIC_NAME, value=data)
                producer.flush()
                print(f"Published data to topic '{TOPIC_NAME}' at {data['fetched_at']}")
            except Exception as e:
                print(f"Failed to send data to Kafka: {e}")
        
        if args.run_once:
            break
        
        # Fetch interval (e.g., every 60 seconds)
        time.sleep(60)

if __name__ == "__main__":
    run_producer()

import json
import os
import sys
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.core.mongodb import MongoDB

# --- Configuration ---
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = "stock_market_data"
GROUP_ID = "stock_consumer_group"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stock_consumer")

def run_consumer():
    """
    Consumes stock data from Kafka and writes it to MongoDB.
    """
    logger.info(f"Connecting to Kafka at {KAFKA_BROKER}...")
    
    # Retry logic for initial connection
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=GROUP_ID,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Successfully connected to Kafka.")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            import time
            time.sleep(5)

    # Initialize MongoDB Connection
    mongo_uri = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DATABASE", "RawData")
    
    if not mongo_uri:
        logger.error("MONGODB_URL or MONGODB_URI environment variable not set.")
        return

    mongo = MongoDB(uri=mongo_uri, db_name=db_name)
    try:
        mongo.connect()
    except Exception as e:
        logger.critical(f"Failed to connect to MongoDB: {e}")
        return

    logger.info("Starting Stock Consumer Loop...")
    
    for message in consumer:
        try:
            data = message.value
            logger.info(f"Received data from {TOPIC_NAME}, fetched at: {data.get('fetched_at', 'unknown')}")
            
            # Write to MongoDB
            # Note: The original implementation wrapped the payload in another "data" key: {"data": payload}
            # We'll maintain that structure for consistency with the frontend.
            mongo.insert(collection_name="Stock_Market", data={"data": data})
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

if __name__ == "__main__":
    run_consumer()

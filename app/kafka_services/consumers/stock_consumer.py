import json
import os
import sys
import logging
from confluent_kafka import Consumer, KafkaError

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
    
    consumer_conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC_NAME])

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
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(msg.error())
                    break
            
            data = json.loads(msg.value().decode('utf-8'))
            logger.info(f"Received data from {TOPIC_NAME}, fetched at: {data.get('fetched_at', 'unknown')}")
            
            # Write to MongoDB
            # Note: The original implementation wrapped the payload in another "data" key: {"data": payload}
            # We'll maintain that structure for consistency with the frontend.
            mongo.insert(collection_name="Stock_Market", data={"data": data})
            
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        logger.info("Stock consumer closed.")

if __name__ == "__main__":
    run_consumer()

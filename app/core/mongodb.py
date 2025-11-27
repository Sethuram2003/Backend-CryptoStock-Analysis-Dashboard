import os
import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.server_api import ServerApi

class MongoDB:
    def __init__(self, uri: str | None, db_name: str):
        """
        Initialize MongoDB connection.
        :param uri: MongoDB connection string (prefer from env in serverless)
        :param db_name: Name of the database to connect to
        """
        self.uri = os.getenv("MONGODB_URI", uri)
        self.db_name = db_name
        self.client: MongoClient | None = None
        self.db = None

    def connect(self):
        """
        Establish a connection to the MongoDB database.
        Reuses a global client across invocations (serverless-friendly).
        """
        global _GLOBAL_MONGO_CLIENT

        if self.db is not None:
            return self.db

        try:
            if "_GLOBAL_MONGO_CLIENT" in globals() and _GLOBAL_MONGO_CLIENT is not None:
                self.client = _GLOBAL_MONGO_CLIENT
            else:
                self.client = MongoClient(
                    self.uri,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=8000,
                    connectTimeoutMS=8000,
                    retryWrites=True,
                    retryReads=True,
                    appname=os.getenv("MONGODB_APPNAME", "CryptoStockIngest"),
                    server_api=ServerApi("1"),
                )
                _GLOBAL_MONGO_CLIENT = self.client

            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            logging.info(f"✅ Connected to MongoDB: {self.db_name}")
            return self.db

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logging.error(f"❌ Could not connect to MongoDB: {e}")
            logging.error(f"Using certifi CA at: {certifi.where()}")
            logging.error("Tip: ensure pymongo[srv] and certifi are installed on Vercel.")
            raise
        except Exception as e:
            logging.exception(f"❌ Unexpected MongoDB error: {e}")
            raise

    def insert(self, collection_name: str, data: dict):
        """
        Insert a single document into the specified collection.
        """
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        try:
            result = self.db[collection_name].insert_one(data)
            logging.info(f"Inserted document ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logging.error(f"Failed to insert document into {collection_name}: {e}")
            raise

    def insert_many(self, collection_name: str, data_list: list[dict]):
        """
        Insert multiple documents into a collection.
        """
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        try:
            result = self.db[collection_name].insert_many(data_list)
            logging.info(f"Inserted {len(result.inserted_ids)} documents.")
            return result.inserted_ids
        except Exception as e:
            logging.error(f"Failed to insert multiple documents into {collection_name}: {e}")
            raise


if __name__ == "__main__":

    uri = "mongodb+srv://praveen:praveen_fishoil@cluster0.tpxrd0x.mongodb.net/RawData?retryWrites=true&w=majority&appName=Cluster0"
    db_name = "RawData"

    mongo = MongoDB(uri, db_name)

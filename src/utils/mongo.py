from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        """
        Initialize MongoDB connection.
        :param uri: MongoDB connection string
        :param db_name: Name of the database to connect to
        """
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """
        Establish a connection to the MongoDB database.
        """
        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')  # test connection
            self.db = self.client[self.db_name]
            logging.info(f"✅ Connected to MongoDB: {self.db_name}")
            return self.db
        except ConnectionFailure as e:
            logging.error(f"❌ Could not connect to MongoDB: {e}")
            raise

    def insert(self, collection_name: str, data: dict):
        """
        Insert a single document into the specified collection.
        :param collection_name: Name of the collection
        :param data: Dictionary representing the document
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            logging.info(f"Inserted document ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logging.error(f"Failed to insert document into {collection_name}: {e}")
            raise

    def insert_many(self, collection_name: str, data_list: list):
        """
        Insert multiple documents into a collection.
        :param collection_name: Name of the collection
        :param data_list: List of documents (dicts)
        """
        if self.db is None:
            raise Exception("Database not connected. Call connect() first.")
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(data_list)
            logging.info(f"Inserted {len(result.inserted_ids)} documents.")
            return result.inserted_ids
        except Exception as e:
            logging.error(f"Failed to insert multiple documents into {collection_name}: {e}")
            raise


uri = "mongodb+srv://praveen:praveen_fishoil@cluster0.tpxrd0x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
db_name = "RawData"

mongo = MongoDB(uri, db_name)
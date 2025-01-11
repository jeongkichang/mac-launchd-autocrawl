import sys
import logging
from pymongo import MongoClient

def connect_to_mongo(uri, database_name, collection_name):
    try:
        client = MongoClient(uri)
        db = client[database_name]
        collection = db[collection_name]
        logging.info(f"Connected to MongoDB: {database_name}.{collection_name}")
        return collection
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

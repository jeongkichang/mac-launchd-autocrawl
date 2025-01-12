import sys
import logging
from pymongo import MongoClient

class MongoConnection:
    _client = None
    _dbs = {}
    _lock = False

    @classmethod
    def get_client(cls, uri):
        if cls._client is None:
            cls._client = MongoClient(uri)
            logging.info("MongoClient created")
        return cls._client

    @classmethod
    def get_db(cls, uri, database_name):
        if database_name not in cls._dbs:
            client = cls.get_client(uri)
            cls._dbs[database_name] = client[database_name]
            logging.info(f"DB cached: {database_name}")
        return cls._dbs[database_name]

    @classmethod
    def get_collection(cls, uri, database_name, collection_name):
        db = cls.get_db(uri, database_name)
        return db[collection_name]

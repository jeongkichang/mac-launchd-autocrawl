import os
import sys
import time
import logging
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from crawler.parser import parse_page

def setup_logger():
    # 로그 설정
    log_file = "/tmp/boot_crawl.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def is_internet_connected(url="https://www.google.com", timeout=3):
    try:
        requests.head(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False

def wait_for_internet(interval=5, retry_delay=5):
    logging.info("Checking internet connection...")
    while True:
        if is_internet_connected():
            logging.info("Internet connected. Proceeding...")
            return
        else:
            logging.warning("Internet not connected. Waiting for retry...")
            time.sleep(retry_delay)

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

def main():
    setup_logger()

    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")

    collection = connect_to_mongo(MONGO_URI, DATABASE_NAME, COLLECTION_NAME)

    wait_for_internet()

    targets = collection.find()

    for target in targets:
        name = target.get("name")

        try:
            results = parse_page(target)
            for item in results:
                logging.info(item)
        except requests.ConnectionError as ce:
            logging.error(f"Connection error while processing {name}: {ce}")
        except Exception as e:
            logging.error(f"Unexpected error while processing {name}: {e}")

if __name__ == "__main__":
    main()

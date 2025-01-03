import os
import sys
import time
import socket
import yaml
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

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, "..", "config")

    real_config = os.path.join(config_dir, "sites.yaml")

    if not os.path.exists(real_config):
        print(f"[ERROR] '{real_config}' 파일이 존재하지 않습니다.")
        print("       설정 파일을 만들어 주신 후 다시 실행해주세요.")
        sys.exit(1)

    # 파일이 존재하면 로드
    with open(real_config, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

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

    config = load_config()
    targets = config.get("crawl_targets", [])

    for target in targets:
        name = target.get("name")
        data_list = target.get("data_to_extract", [])

        for data_item in data_list:
            data_name = data_item.get("data_name")
            print(f"\n== Crawling {name} :: {data_name} ==")

            MAX_RETRIES = 5
            retry_count = 0

            while retry_count < MAX_RETRIES:
                try:
                    results = parse_page(data_item)
                    for item in results:
                        logging.info(item)
                    break

                except requests.ConnectionError as ce:
                    retry_count += 1
                    logging.error(f"Connection error (attempt {retry_count}/{MAX_RETRIES}): {ce}")
                    if retry_count < MAX_RETRIES:
                        logging.info("Re-checking internet connection...")
                        wait_for_internet()
                    else:
                        logging.error("Max retries reached. Exiting for this data item.")
                        break
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    break

            for item in results:
                logging.info(item)

if __name__ == "__main__":
    main()

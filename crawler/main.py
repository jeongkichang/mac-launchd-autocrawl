import os
import sys
import time
import socket
import yaml
import logging
import requests
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

def main():
    setup_logger()

    wait_for_internet()

    config = load_config()
    targets = config.get("crawl_targets", [])

    for target in targets:
        name = target.get("name")
        data_list = target.get("data_to_extract", [])

        for data_item in data_list:
            data_name = data_item.get("data_name")
            print(f"\n== Crawling {name} :: {data_name} ==")

            # 혹시 크롤링 도중에 인터넷이 다시 끊길 수도 있으므로
            # 추가로 예외처리를 넣고, 끊기면 다시 연결 기다리게끔 구성.
            while True:
                try:
                    results = parse_page(data_item)
                    for item in results:
                        logging.info(item)
                    break

                except requests.ConnectionError as ce:
                    logging.error(f"Connection error: {ce}")
                    logging.info("Re-checking internet connection...")
                    wait_for_internet()
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    break

            for item in results:
                logging.info(item)

if __name__ == "__main__":
    main()

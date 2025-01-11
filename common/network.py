import time
import logging
import requests

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

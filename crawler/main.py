import os
import sys
import time
import logging
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from crawler.parser import parse_page
from bs4 import BeautifulSoup
import google.generativeai as genai

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

def get_removed_html_tag_from_content(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
        try:
            resp = requests.get(url)
        except requests.exceptions.RequestException:
            url = url.replace("https://", "http://")
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style", "head", "title"]):
        tag.decompose()

    return soup.get_text(separator="\n", strip=True)

def get_refined_swim_info(removed_html_tag_from_content):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the .env file")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    text = f"""
    <content></content> 내용을 참고해서 자유 수영에 대한 정보를 정리해줘.
    1회 이용에 대한 정보만 정리해줘.
    보통, 1회 이용료는 20,000원이 넘지 않아. 그것들은 제외해줘.
    같은 시간대에 요금이 상이하면, 상이한대로 시간과 함께 구별해서 모두 표기해줘.
    아래와 같은 형식으로 만들어줘.

    ex.
    월 : 10:00-10:50 / 성인 54,500 / 중고생 40,500
    월 : 11:00-12:50 / 성인 54,500 / 중고생 40,500
    ...
    화 : 11:00-12:50 / 성인 54,500 / 중고생 40,500
    ...

    <content>
    {removed_html_tag_from_content}
    </content>
    """

    response = model.generate_content(text)
    print(response.text)

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
        url = target.get("url")
        removed_html_content = get_removed_html_tag_from_content(url)
        get_refined_swim_info(removed_html_content)

if __name__ == "__main__":
    main()

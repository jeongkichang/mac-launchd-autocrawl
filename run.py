import os
from dotenv import load_dotenv

from common.logger import setup_logger
from common.network import wait_for_internet

from db.mongo import connect_to_mongo

from crawler.content import get_removed_html_tag_from_content
from crawler.generator import get_refined_swim_info

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
        refined_info = get_refined_swim_info(removed_html_content)

        print("========== Refined Swim Info ==========")
        print(refined_info)
        print("=======================================")

if __name__ == "__main__":
    main()

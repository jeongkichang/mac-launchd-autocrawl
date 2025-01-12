import os
from dotenv import load_dotenv
import json

from common.logger import setup_logger
from common.network import wait_for_internet

from db.mongo_singleton import MongoConnection

from crawler.content import get_removed_html_tag_from_content
from crawler.generator import get_refined_swim_info

def main():
    setup_logger()

    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    swimming_pool_collection = MongoConnection.get_collection(MONGO_URI, DATABASE_NAME, "swimming_pool")
    daily_swim_schedule_collection = MongoConnection.get_collection(MONGO_URI, DATABASE_NAME, "daily_swim_schedule")

    wait_for_internet()

    targets = swimming_pool_collection.find()

    for target in targets:
        url = target.get("url")
        pool_code = target.get("code", "")

        removed_html_content = get_removed_html_tag_from_content(url)
        refined_info_json_string = get_refined_swim_info(removed_html_content)

        try:
            refined_info_json = json.loads(refined_info_json_string)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            continue

        if isinstance(refined_info_json, list):
            for doc in refined_info_json:
                doc["pool_code"] = pool_code
            if refined_info_json:
                result = daily_swim_schedule_collection.insert_many(refined_info_json)
                print(f"Inserted {len(result.inserted_ids)} documents for code {pool_code}")
            else:
                print(f"No documents to insert for code {pool_code}")
        elif isinstance(refined_info_json, dict):
            refined_info_json["pool_code"] = pool_code
            result = daily_swim_schedule_collection.insert_one(refined_info_json)
            print(f"Inserted 1 document for code {pool_code}")
        else:
            print("refined_info_json is not a list or dict. Skipped insertion.")

if __name__ == "__main__":
    main()

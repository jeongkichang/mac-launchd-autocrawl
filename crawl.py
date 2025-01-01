#!/usr/bin/env python3
import datetime

def main():
    with open("/tmp/boot_crawl.log", "a") as f:
        f.write(f"[{datetime.datetime.now()}] 크롤러 실행 완료!\n")

if __name__ == "__main__":
    main()

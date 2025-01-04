import requests
from bs4 import BeautifulSoup

def parse_free_swim_single_use(url, table_selector, row_selector, filter_keyword):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
        try:
            resp = requests.get(url)
        except requests.exceptions.RequestException:
            url = url.replace("https://", "http://")

    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    free_swim_header = soup.find("h2", string="자유 수영")
    if not free_swim_header:
        print("Cannot find the '자유 수영' section.")
        return []

    tables = free_swim_header.find_all_next("table")

    if len(tables) < 2:
        print("Could not find the second table after '자유 수영' header.")
        return []

    target_table = tables[1]

    rows = target_table.select(row_selector)

    results = []
    for row in rows:
        cols = row.find_all(["th", "td"])
        if len(cols) < 6:
            continue

        # 테이블 구조상 [구분, 강좌명, 요 일, 시간, 정원, 대상 및 회비] (… 비고는 없으니 len 6일 수도)
        division = cols[0].get_text(strip=True)
        course_name = cols[1].get_text(strip=True)
        day_of_week = cols[2].get_text(strip=True)
        time_range = cols[3].get_text(strip=True)
        capacity = cols[4].get_text(strip=True)
        fee_info = cols[5].get_text(strip=True)

        # (C) filter_keyword 로 필터링 → "(1회)"가 fee_info에 들어 있으면 추출
        if filter_keyword in fee_info:
            results.append({
                "division": division,
                "course_name": course_name,
                "day_of_week": day_of_week,
                "time_range": time_range,
                "capacity": capacity,
                "fee_info": fee_info,
            })

    return results


def parse_page(data_config):
    url = data_config.get("url")
    table_selector = data_config.get("table_selector")
    row_selector = data_config.get("row_selector")
    filter_keyword = data_config.get("filter_keyword")

    return parse_free_swim_single_use(url, table_selector, row_selector, filter_keyword)

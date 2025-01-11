import requests
from bs4 import BeautifulSoup

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

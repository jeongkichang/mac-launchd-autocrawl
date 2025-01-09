import requests
from bs4 import BeautifulSoup

url = "example.com"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

for tag in soup(["script", "style", "head", "title"]):
    tag.decompose()

text = soup.get_text(separator="\n", strip=True)
print(text)

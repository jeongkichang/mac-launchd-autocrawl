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

# Please do the following

# Extract only the days and times when “Daily free swim (1 entry)” is available from this text.

# Please also extract the days and times of the week when “Adult 1-time fee” and “Child (or youth) 1-time fee” are available.

# If the original text has separate rates for “children,” “teens,” “middle schoolers,” “high schoolers,” etc., please combine them into one category (e.g., children).

# The result should be formatted according to the example below.

# Monday: 09:00 - 10:00 / Adult: 7,000 | Child: 3,500
# Monday: 10:00 - 11:00 / Adult: 7,000 | Child: 3,500
# Tuesday : 15:00 - 16:00 / Adult : 7,000 | Child : 3,500
# Day of the week : Start time - End time / Adult : ___ | Child : ___

# Ignore or remove any information about other lessons or packages available, pools, number of lessons, etc. that is included in the text, and leave only the “Daily Free Swim” information.

# You may have different pricing units, such as “Adult 4,250 won / Student 2,500 won (1 time)”. In this case, please only list two rates, “Adult” and “Child”, and use the lowest of the middle school, high school, and child rates for children.

# Even if the rates are slightly different from the original, please only list them in the form “Adult: ~$1 | Child: ~$1”.

# If you have multiple time slots for each day of the week, please split the line to list them all, as shown in the example.

# We'll paste the original text below. Please extract only the information related to “Daily free swim (1 entry)” from the original content.
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://zeus.com2us.com/news/notice"

headers = {
    "User-Agent": "Mozilla/5.0"
}

for notice_id in range(2650, 2635, -1):

    url = f"{BASE_URL}/{notice_id}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""

    print("공지번호:", notice_id)
    print("TITLE:", title)
    print("-" * 50)

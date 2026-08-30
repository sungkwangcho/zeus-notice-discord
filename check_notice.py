import requests

BASE_URL = "https://zeus.com2us.com/news/notice"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 테스트용: 최근 번호 구간 확인
for notice_id in range(2650, 2635, -1):

    url = f"{BASE_URL}/{notice_id}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    print(
        notice_id,
        response.status_code,
        len(response.text)
    )

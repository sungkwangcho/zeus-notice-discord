import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://zeus.com2us.com/news/notice"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_notice(notice_id):

    url = f"{BASE_URL}/{notice_id}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    if not soup.title:
        return None

    title = soup.title.get_text(strip=True)

    # 존재하지 않는 공지는 기본 제목으로 반환됨
    if title == "공지사항 | 제우스: 오만의 신":
        return None

    # 뒤에 붙는 사이트명 제거
    title = title.replace(
        " | 제우스: 오만의 신",
        ""
    )

    return {
        "id": notice_id,
        "title": title,
        "url": url
    }


def send_discord(notice):

    message = {
        "content":
            f"🚨 **제우스 신규 공지**\n\n"
            f"**{notice['title']}**\n\n"
            f"📢 {notice['url']}"
    }

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=message,
        timeout=10
    )

    print(
        "Discord 응답:",
        response.status_code
    )


# 마지막으로 확인한 실제 공지 번호
with open(
    "last_notice.txt",
    "r",
    encoding="utf-8"
) as f:
    last_notice_id = int(
        f.read().strip()
    )

print(
    "마지막 공지 번호:",
    last_notice_id
)

new_notices = []

# 이후 번호 30개 확인
for notice_id in range(
    last_notice_id + 1,
    last_notice_id + 31
):

    notice = get_notice(
        notice_id
    )

    if notice:

        print(
            "신규 공지 발견:",
            notice["id"],
            notice["title"]
        )

        new_notices.append(
            notice
        )


# 발견된 공지가 있으면 순서대로 Discord 전송
if new_notices:

    for notice in new_notices:
        send_discord(
            notice
        )

    latest_id = max(
        notice["id"]
        for notice in new_notices
    )

    with open(
        "last_notice.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            str(latest_id)
        )

    print(
        "마지막 공지 번호 갱신:",
        latest_id
    )

else:

    print(
        "신규 공지 없음"
    )

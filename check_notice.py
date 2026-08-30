import os
import asyncio
import tempfile
import requests
import discord

from bs4 import BeautifulSoup
from gtts import gTTS


BASE_URL = "https://zeus.com2us.com/news/notice"

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_VOICE_CHANNEL_ID = int(
    os.environ["DISCORD_VOICE_CHANNEL_ID"]
)

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


def get_notice_type(title):
    if "긴급" in title or "점검" in title:
        return {
            "icon": "🚨",
            "category": "긴급 공지",
            "voice_text": "제우스 긴급 공지가 등록되었습니다. 채팅을 확인해주세요."
        }

    elif "업데이트" in title or "패치" in title:
        return {
            "icon": "🔧",
            "category": "업데이트",
            "voice_text": "제우스 업데이트 공지가 등록되었습니다. 채팅을 확인해주세요."
        }

    elif "이벤트" in title:
        return {
            "icon": "🎁",
            "category": "이벤트",
            "voice_text": "제우스 이벤트 공지가 등록되었습니다. 채팅을 확인해주세요."
        }

    else:
        return {
            "icon": "📢",
            "category": "일반 공지",
            "voice_text": "제우스 신규 공지가 등록되었습니다. 채팅을 확인해주세요."
        }


def send_discord(notice):
    notice_type = get_notice_type(
        notice["title"]
    )

    payload = {
        "username": "ZEUS Notice Bot",
        "content": notice_type["voice_text"],
        "embeds": [
            {
                "title": f'{notice_type["icon"]} 제우스 신규 공지',
                "description": f'**{notice["title"]}**',
                "fields": [
                    {
                        "name": "분류",
                        "value": notice_type["category"],
                        "inline": True
                    },
                    {
                        "name": "공지번호",
                        "value": str(notice["id"]),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "ZEUS : 오만의 신"
                }
            }
        ]
    }

    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json=payload,
        timeout=10
    )

    print(
        "Discord 응답:",
        response.status_code
    )


async def play_voice_alert(text):
    intents = discord.Intents.default()

    client = discord.Client(
        intents=intents
    )

    @client.event
    async def on_ready():
        print(
            "Voice Bot 로그인:",
            client.user
        )

        channel = client.get_channel(
            DISCORD_VOICE_CHANNEL_ID
        )

        if channel is None:
            print(
                "음성 채널을 찾지 못했습니다."
            )
            await client.close()
            return

        voice_client = None
        audio_path = None

        try:
            print(
                "음성 채널 접속:",
                channel.name
            )

            voice_client = await channel.connect()

            with tempfile.NamedTemporaryFile(
                suffix=".mp3",
                delete=False
            ) as temp_file:
                audio_path = temp_file.name

            tts = gTTS(
                text=text,
                lang="ko"
            )

            tts.save(
                audio_path
            )

            audio = discord.FFmpegPCMAudio(
                audio_path
            )

            voice_client.play(
                audio
            )

            while voice_client.is_playing():
                await asyncio.sleep(0.5)

            print(
                "음성 알림 재생 완료"
            )

        except Exception as e:
            print(
                "음성 알림 오류:",
                str(e)
            )

        finally:
            if voice_client is not None:
                await voice_client.disconnect()

            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

            await client.close()

    await client.start(
        DISCORD_BOT_TOKEN
    )


def send_voice_alert(notice):
    notice_type = get_notice_type(
        notice["title"]
    )

    asyncio.run(
        play_voice_alert(
            notice_type["voice_text"]
        )
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


# 신규 공지가 있으면 채팅 + 음성 알림
if new_notices:

    for notice in new_notices:
        # Discord 채팅 알림
        send_discord(
            notice
        )

        # Discord 음성 알림
        send_voice_alert(
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

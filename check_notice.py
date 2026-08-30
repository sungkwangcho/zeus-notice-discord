import os
import requests

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

message = {
    "content": "🔔 제우스 공지 봇 테스트 알림입니다."
}

response = requests.post(
    webhook_url,
    json=message
)

print("Discord 응답 코드:", response.status_code)

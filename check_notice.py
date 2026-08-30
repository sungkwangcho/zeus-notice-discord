import requests

url = "https://zeus.com2us.com/news/notice"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=10
)

print("HTTP 상태코드:", response.status_code)
print("응답 길이:", len(response.text))

print("----- 응답 일부 -----")
print(response.text[:1000])

import requests
import json

url = "http://127.0.0.1:8045/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-9de6f510828b4f73a2acef35ed5f846b",
    "Content-Type": "application/json"
}
payload = {
    "model": "gemini-3-pro-image",
    "messages": [{"role": "user", "content": "Draw a futuristic city"}],
    "extra_body": { "size": "1024x1024" }
}

print(f"POSTing to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Raw Response: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

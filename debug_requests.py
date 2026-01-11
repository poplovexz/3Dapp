import requests
import json

url = "http://127.0.0.1:8045/v1beta/models/gemini-3-pro-image:generateContent?key=sk-9de6f510828b4f73a2acef35ed5f846b"

payload = {
    "contents": [{
        "parts": [{"text": "Hello"}]
    }]
}

print(f"POSTing to {url}...")
try:
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Body Preview: {response.text[:500]}")
    
    try:
        data = response.json()
        print("JSON parse successful.")
    except Exception as e:
        print(f"JSON parse failed: {e}")
except Exception as e:
    print(f"Connection failed: {e}")

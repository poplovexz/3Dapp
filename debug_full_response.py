import requests
import json

url = "http://127.0.0.1:8045/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-9de6f510828b4f73a2acef35ed5f846b",
    "Content-Type": "application/json"
}
payload = {
    "model": "gemini-3-pro-image",
    "messages": [{"role": "user", "content": "Draw a cute little bird"}],
    "extra_body": { "size": "1024x1024" }
}

print(f"POSTing to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    content = response.content
    print(f"Content Length (bytes): {len(content)}")
    print(f"Content (first 100 bytes): {content[:100]}")
    
    if len(content) == 0:
        print("WARNING: Response body is empty!")
        
except Exception as e:
    print(f"Connection error: {e}")

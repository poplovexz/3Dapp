import requests
import base64

# Create a small base64 image
img_data = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKwjqAAAAABJRU5ErkJggg=="
b64_img = base64.b64encode(img_data).decode('utf-8')

payload = {
    "azimuth": 0,
    "elevation": 0,
    "distance": 1.0,
    "image": b64_img
}

try:
    print("Sending request to http://127.0.0.1:8000/generate ...")
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

import requests
import base64

# Create a small white pixel image
small_image_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAAAgABKlx+MAAAAABJRU5ErkJggg=="

payload = {
    "azimuth": 0,
    "elevation": 0,
    "distance": 1.0,
    "image": small_image_b64
}

try:
    print("Sending request to backend...")
    response = requests.post("http://127.0.0.1:8000/generate", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")

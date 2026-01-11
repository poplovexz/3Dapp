import requests
import time

print("Pinging backend...")
start = time.time()
try:
    # Just a simple request to check responsiveness
    response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
    print(f"Response: {response.status_code}")
    print(f"Time: {time.time() - start:.2f}s")
except Exception as e:
    print(f"Error/Timeout: {e}")

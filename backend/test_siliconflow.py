import httpx
import asyncio

async def test_siliconflow():
    request_id = "gct55syfls4w"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.siliconflow.cn/v1/videos/{request_id}",
                headers={
                    "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg"
                },
                timeout=10.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_siliconflow())

import httpx
import asyncio

async def test_correct_api():
    request_id = "qksu14mrncn5"
    
    async with httpx.AsyncClient() as client:
        print("使用正确的 API 调用方式查询状态...")
        response = await client.post(
            "https://api.siliconflow.cn/v1/video/status",
            headers={
                "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg",
                "Content-Type": "application/json"
            },
            json={"requestId": request_id},
            timeout=10.0
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 查询成功!")
            print(f"状态: {data.get('status')}")
            print(f"完整响应: {data}")

asyncio.run(test_correct_api())

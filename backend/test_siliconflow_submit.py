import httpx
import asyncio
import base64

async def test_siliconflow_submit():
    # 创建一个测试图片 (1x1 像素的白色 JPEG)
    test_image_b64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA//2Q=="
    
    payload = {
        "model": "Wan-AI/Wan2.2-I2V-A14B",
        "prompt": "natural movement, smooth motion",
        "image_size": "1280x720",
        "image": f"data:image/jpeg;base64,{test_image_b64}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("正在提交视频生成请求到硅基流动...")
            response = await client.post(
                "https://api.siliconflow.cn/v1/video/submit",
                headers={
                    "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            print(f"\n=== 硅基流动 API 响应 ===")
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应体: {response.text}")
            print(f"========================\n")
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("requestId")
                print(f"✅ 提交成功! requestId: {request_id}")
            else:
                print(f"❌ 提交失败! 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")

asyncio.run(test_siliconflow_submit())

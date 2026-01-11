import httpx
import asyncio
import time

async def test_siliconflow_status():
    request_id = "qksu14mrncn5"  # 刚才提交的任务ID
    
    async with httpx.AsyncClient() as client:
        for i in range(5):  # 查询5次
            try:
                print(f"\n第 {i+1} 次查询状态...")
                response = await client.get(
                    f"https://api.siliconflow.cn/v1/videos/{request_id}",
                    headers={
                        "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg"
                    },
                    timeout=10.0
                )
                
                print(f"状态码: {response.status_code}")
                print(f"响应体: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    print(f"当前状态: {status}")
                    
                    if status == "Completed":
                        print(f"✅ 视频生成完成!")
                        print(f"视频链接: {data.get('videos', [{}])[0].get('url')}")
                        break
                
                await asyncio.sleep(3)  # 等待3秒再查询
                
            except Exception as e:
                print(f"❌ 查询出错: {e}")

asyncio.run(test_siliconflow_status())

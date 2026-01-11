import httpx
import asyncio
import base64
import os
from PIL import Image
import io

async def full_test():
    print("=== 硅基流动完整流程测试 ===\n")
    
    # 1. 准备图片
    print("步骤 1: 准备测试图片...")
    
    # 创建一个简单的测试图片 (500x500 白底红圈)
    img = Image.new('RGB', (500, 500), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 400, 400], fill='red')
    
    # 转换为 base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    print(f"✅ 图片准备完成 (大小: {len(img_b64)} 字符)\n")
    
    # 2. 提交视频生成请求
    print("步骤 2: 提交视频生成请求...")
    
    payload = {
        "model": "Wan-AI/Wan2.2-I2V-A14B",
        "prompt": "natural movement, smooth motion",
        "image_size": "1280x720",
        "image": f"data:image/jpeg;base64,{img_b64}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            submit_response = await client.post(
                "https://api.siliconflow.cn/v1/video/submit",
                headers={
                    "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            print(f"提交响应状态码: {submit_response.status_code}")
            print(f"提交响应内容: {submit_response.text}\n")
            
            if submit_response.status_code != 200:
                print(f"❌ 提交失败!")
                return
            
            data = submit_response.json()
            request_id = data.get("requestId")
            print(f"✅ 提交成功! requestId: {request_id}\n")
            
            # 3. 轮询状态
            print("步骤 3: 轮询视频生成状态...")
            
            for attempt in range(60):  # 最多等待 3 分钟
                await asyncio.sleep(3)
                
                status_response = await client.post(
                    "https://api.siliconflow.cn/v1/video/status",
                    headers={
                        "Authorization": "Bearer sk-ukebjdpbnsqmimfgfyoylqmeawxffvnegsburwzopnjnifzg",
                        "Content-Type": "application/json"
                    },
                    json={"requestId": request_id},
                    timeout=10.0
                )
                
                if status_response.status_code != 200:
                    print(f"查询失败 (attempt {attempt + 1}): {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                status = status_data.get("status")
                
                print(f"[{attempt + 1}/60] 状态: {status}")
                
                if status == "Succeed":
                    print(f"\n✅ 视频生成完成!")
                    
                    # 4. 下载视频
                    results = status_data.get("results", {})
                    videos = results.get("videos", [])
                    video_url = videos[0].get("url") if videos else None
                    
                    if video_url:
                        print(f"\n步骤 4: 下载视频...")
                        print(f"视频链接: {video_url}")
                        
                        video_response = await client.get(video_url, timeout=60.0)
                        
                        if video_response.status_code == 200:
                            output_path = "test_siliconflow_video.mp4"
                            with open(output_path, "wb") as f:
                                f.write(video_response.content)
                            
                            file_size = len(video_response.content)
                            print(f"✅ 视频下载成功! 文件大小: {file_size} 字节")
                            print(f"保存位置: {os.path.abspath(output_path)}")
                        else:
                            print(f"❌ 视频下载失败: {video_response.status_code}")
                    else:
                        print(f"❌ 未找到视频链接")
                    
                    break
                
                elif status == "Failed":
                    print(f"\n❌ 视频生成失败!")
                    print(f"原因: {status_data.get('reason')}")
                    break
            
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(full_test())

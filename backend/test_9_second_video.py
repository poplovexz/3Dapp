import httpx
import asyncio
import base64
import os
from PIL import Image
import io

async def test_9_second_video():
    print("=== 测试硅基流动 9 秒视频生成 ===\n")
    
    # 1. 准备测试图片
    print("步骤 1: 准备测试图片...")
    
    # 创建一个简单的测试图片 (1280x720 渐变背景)
    img = Image.new('RGB', (1280, 720), color='skyblue')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # 绘制一个圆形
    draw.ellipse([440, 160, 840, 560], fill='orange', outline='red', width=5)
    
    # 添加文字
    try:
        draw.text((640, 360), "9秒测试", fill='white', anchor='mm')
    except:
        pass  # 如果没有字体,跳过文字
    
    # 转换为 base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    print(f"✅ 图片准备完成 (大小: {len(img_b64)} 字符)\n")
    
    # 2. 提交 9 秒视频生成请求
    print("步骤 2: 提交 9 秒视频生成请求...")
    print("参数配置:")
    print("  - num_frames: 144")
    print("  - frames_per_second: 16")
    print("  - 计算时长: 144 / 16 = 9 秒\n")
    
    payload = {
        "model": "Wan-AI/Wan2.2-I2V-A14B",
        "prompt": "smooth rotation, natural movement, cinematic motion",
        "image_size": "1280x720",
        "image": f"data:image/jpeg;base64,{img_b64}",
        "num_frames": 144,  # 9 秒视频
        "frames_per_second": 16
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
            print("步骤 3: 轮询视频生成状态 (9秒视频可能需要更长处理时间)...")
            
            for attempt in range(100):  # 最多等待 5 分钟
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
                
                print(f"[{attempt + 1}/100] 状态: {status}")
                
                if status == "Succeed":
                    print(f"\n✅ 9秒视频生成完成!")
                    
                    # 4. 下载视频
                    results = status_data.get("results", {})
                    videos = results.get("videos", [])
                    video_url = videos[0].get("url") if videos else None
                    
                    if video_url:
                        print(f"\n步骤 4: 下载视频...")
                        print(f"视频链接: {video_url}")
                        
                        video_response = await client.get(video_url, timeout=60.0)
                        
                        if video_response.status_code == 200:
                            output_path = "test_9_second_video.mp4"
                            with open(output_path, "wb") as f:
                                f.write(video_response.content)
                            
                            file_size = len(video_response.content)
                            print(f"✅ 9秒视频下载成功!")
                            print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
                            print(f"保存位置: {os.path.abspath(output_path)}")
                            print(f"\n🎬 请播放视频确认时长是否为 9 秒")
                        else:
                            print(f"❌ 视频下载失败: {video_response.status_code}")
                    else:
                        print(f"❌ 未找到视频链接")
                    
                    break
                
                elif status == "Failed":
                    print(f"\n❌ 视频生成失败!")
                    print(f"错误信息: {status_data}")
                    break
            
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_9_second_video())

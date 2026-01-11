import google.generativeai as genai
import os

# 配置 API
genai.configure(
    api_key="sk-9de6f510828b4f73a2acef35ed5f846b",
    transport='rest',
    client_options={'api_endpoint': 'http://127.0.0.1:8045'}
)

print("Testing model connection...")
try:
    model = genai.GenerativeModel('gemini-3-pro-image')
    print("Generating content...")
    response = model.generate_content("A cute robot")
    
    print("\n--- Response Info ---")
    print(f"Has parts: {bool(response.parts)}")
    print(f"Has text: {bool(response.text) if hasattr(response, 'text') else 'No text attr'}")
    
    if hasattr(response, 'text'):
        print(f"Response Text prefix: {response.text[:100]}")
    
    # 检查是否包含图片数据
    if response.parts:
        for part in response.parts:
            print(f"Part: {part}")
            
except Exception as e:
    print(f"\nError occurred: {e}")

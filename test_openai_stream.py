from openai import OpenAI
import os

client = OpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="sk-9de6f510828b4f73a2acef35ed5f846b"
)

print("Testing STREAMING generation...")

try:
    response = client.chat.completions.create(
        model="gemini-3-pro-image",
        extra_body={ "size": "1024x1024" },
        messages=[{
            "role": "user",
            "content": "Draw a cute little bird"
        }],
        stream=True
    )
    
    print("Stream detected. Iterating chunks...")
    full_content = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            print(f"Chunk: {delta}")
            full_content += delta
            
    print(f"\nFinal Content: {full_content}")
    
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")

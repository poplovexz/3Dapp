from openai import OpenAI
import os

client = OpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="sk-9de6f510828b4f73a2acef35ed5f846b"
)

print("Testing simple generation: 'Draw a chute little bird'...")

try:
    response = client.chat.completions.create(
        model="gemini-3-pro-image",
        extra_body={ "size": "1024x1024" },
        messages=[{
            "role": "user",
            "content": "Draw a cute little bird"
        }]
    )
    
    print("\n--- Response ---")
    print(f"Response Object: {response}")
    content = response.choices[0].message.content
    print(f"Content: {content}")
    
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")

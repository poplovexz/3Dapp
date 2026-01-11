import os
import base64
import io
import shutil
import subprocess
import glob
import re
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from PIL import Image

# Configuration
FFMPEG_PATH = r"e:\ffmpeg\bin\ffmpeg.exe"
OUTPUT_DIR = "outputs"
TEMP_DIR = "temp_frames"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Async OpenAI Client
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8045/v1",
    api_key="sk-9de6f510828b4f73a2acef35ed5f846b"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated videos
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

class GenerateRequest(BaseModel):
    azimuth: float
    elevation: float
    distance: float
    image: str | None = None
    bg_style: str = "default"

class Generate360Request(BaseModel):
    duration: float = 3.0  # seconds
    fps: int = 24
    elevation: float
    distance: float
    image: str | None = None
    bg_style: str = "default"

def get_bg_prompt(style: str) -> str:
    if style == "white_studio":
        return ", solid white background, clean studio backdrop, no background objects, infinite white environment"
    elif style == "green_screen":
        return ", solid green chroma key background, hex code #00FF00, flat color background, no shadows on wall"
    elif style == "dark_studio":
        return ", solid dark grey background, professional studio lighting, dark mood"
    return ""

def get_angle_keywords(azimuth: float, elevation: float, distance: float) -> str:
    # Azimuth Mapping
    az = azimuth % 360
    az_kw = "front view"
    if 22.5 <= az < 67.5:
        az_kw = "front-right quarter view"
    elif 67.5 <= az < 112.5:
        az_kw = "right side view"
    elif 112.5 <= az < 157.5:
        az_kw = "back-right quarter view"
    elif 157.5 <= az < 202.5:
        az_kw = "back view"
    elif 202.5 <= az < 247.5:
        az_kw = "back-left quarter view"
    elif 247.5 <= az < 292.5:
        az_kw = "left side view"
    elif 292.5 <= az < 337.5:
        az_kw = "front-left quarter view"
        
    # Elevation Mapping
    el_kw = "eye-level shot"
    if elevation <= -15:
        el_kw = "low-angle shot"
    elif elevation >= 45:
        el_kw = "high-angle shot"
    elif elevation >= 15:
        el_kw = "elevated shot"
        
    # Distance Mapping
    dist_kw = "medium shot"
    if distance < 0.8:
        dist_kw = "close-up"
    elif distance > 1.2:
        dist_kw = "wide shot"
        
    return f"{az_kw} {el_kw} {dist_kw}"

async def generate_single_frame(prompt: str, image_b64: str | None) -> str | None:
    """Returns base64 image string or None if failed"""
    try:
        messages = [{"role": "user", "content": prompt}]
        
        if image_b64:
             # Clean base64 header
             if "," in image_b64:
                _, encoded = image_b64.split(",", 1)
             else:
                encoded = image_b64
                
             messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded}"
                    }
                }
             ]
             
        # Async call
        stream_response = await client.chat.completions.create(
             model="gemini-3-pro-image",
             extra_body={ "size": "1024x1024" },
             messages=messages,
             stream=True
        )
        
        result_content = ""
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                result_content += chunk.choices[0].delta.content
                
        # Extract Logic (Markdown or Raw)
        data_uri_pattern = r"\((data:image\/[a-zA-Z]+;base64,[^\)]+)\)"
        match = re.search(data_uri_pattern, result_content)
        if match:
            return match.group(1).split(",")[1] # Return pure base64
        
        # Raw base64 check
        if len(result_content) > 1000 and " " not in result_content[:100] and not result_content.strip().startswith("data:"):
             return result_content.strip() # Return pure base64
             
        return None
    except Exception as e:
        print(f"Error generating frame: {e}")
        return None


# Helper for standardizing image
def normalize_to_jpeg(base64_str: str) -> str:
    try:
        # Strip header if exists
        idx = base64_str.find(",")
        if idx != -1:
            raw_data = base64_str[idx+1:]
        else:
            raw_data = base64_str
            
        image_data = base64.b64decode(raw_data)
        img = Image.open(io.BytesIO(image_data))
        img = img.convert("RGB") # Remove alpha if any, standard compatible
        
        out_buffer = io.BytesIO()
        img.save(out_buffer, format="JPEG", quality=95)
        
        return "data:image/jpeg;base64," + base64.b64encode(out_buffer.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Normalization failed: {e}")
        # Fallback to simple header prepend
        if base64_str.startswith("/9j/"):
             return f"data:image/jpeg;base64,{base64_str}"
        return f"data:image/png;base64,{base64_str}"

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    try:
        # Prompt Construction with Head Locking
        angle_desc = get_angle_keywords(request.azimuth, request.elevation, request.distance)
        bg_desc = get_bg_prompt(request.bg_style)
        
        # FORCE HEAD CONSISTENCY and BACKGROUND:
        full_prompt = (
            f"<sks> {angle_desc}, "
            f"consistent pose, static action, no pose change, "
            f"fixed head position, head facing relative to body, not looking at camera"
            f"{bg_desc}"
        )
        
        print(f"Generating single: {full_prompt}")
        
        messages = [{"role": "user", "content": full_prompt}]
        if request.image:
             if "," in request.image:
                _, encoded = request.image.split(",", 1)
             else:
                encoded = request.image
             messages[0]["content"] = [
                {"type": "text", "text": full_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
             ]

        stream_response = await client.chat.completions.create(
             model="gemini-3-pro-image",
             extra_body={ "size": "1024x1024" },
             messages=messages,
             stream=True
        )
        
        result_content = ""
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                result_content += chunk.choices[0].delta.content
        
        # New Processing Logic
        data_uri_pattern = r"\((data:image\/[a-zA-Z]+;base64,[^\)]+)\)"
        match = re.search(data_uri_pattern, result_content)
        if match:
             raw_b64 = match.group(1)
        elif len(result_content) > 1000 and " " not in result_content[:100] and not result_content.startswith("data:"):
             raw_b64 = result_content
        else:
             raw_b64 = None

        if raw_b64:
            # Normalize to standard JPEG and Ensure header
            result_content = normalize_to_jpeg(raw_b64)
        else:
            result_content = None # Ensure result_content is None if no valid b64 found

        return {"result": result_content, "constructed_prompt": full_prompt}

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-360")
async def generate_video(request: Generate360Request):
    try:
        # 1. Cleanup Temp
        for f in glob.glob(f"{TEMP_DIR}/*"):
            os.remove(f)
            
        total_frames = int(request.duration * request.fps)
        angle_step = 360 / total_frames
        
        print(f"Starting 360 generation: {total_frames} frames, {request.fps} fps")
        
        bg_desc = get_bg_prompt(request.bg_style)
        
        for i in range(total_frames):
            azimuth = i * angle_step
            angle_desc = get_angle_keywords(azimuth, request.elevation, request.distance)
            prompt = (
                f"<sks> {angle_desc} consistent pose, static action, no pose change"
                f"{bg_desc}"
            )
            
            print(f"Generating Frame {i+1}/{total_frames} (Azimuth: {azimuth:.1f})...")
            
            # Using async generation now
            img_b64 = await generate_single_frame(prompt, request.image)
            
            if img_b64:
                # Save to file
                img_data = base64.b64decode(img_b64.split(",", 1)[1] if "," in img_b64 else img_b64)
                with open(f"{TEMP_DIR}/frame_{i:04d}.jpg", "wb") as f:
                    f.write(img_data)
            else:
                print(f"Failed to generate frame {i}")
                if i > 0:
                    shutil.copy(f"{TEMP_DIR}/frame_{i-1:04d}.jpg", f"{TEMP_DIR}/frame_{i:04d}.jpg")
        
        # 2. Stitch with FFMPEG
        output_filename = "result_360.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
        cmd = [
            FFMPEG_PATH,
            "-r", str(request.fps),
            "-i", f"{TEMP_DIR}/frame_%04d.jpg",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        print(f"Running FFMPEG: {' '.join(cmd)}")
        # FFMPEG is CPU bound, run in threadpool to avoid blocking loop? 
        # Actually subprocess.run blocks the loop. 
        # Better to run in executor or use asyncio.create_subprocess_exec (but run_in_threadpool is easier for now)
        # For simplicity in this fix, we stick to sync subprocess because video gen is the last step and long anyway.
        # But we could make it async.
        
        subprocess.run(cmd, check=True)
        
        video_url = f"http://127.0.0.1:8000/outputs/{output_filename}"
        return {"video_url": video_url, "message": "Video generated successfully"}

    except Exception as e:
        print(f"Video Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

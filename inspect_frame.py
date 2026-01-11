try:
    with open(r"e:\duanshiping\camera_tool\backend\temp_frames\frame_0000.png", "rb") as f:
        data = f.read(100)
    print(f"Hex: {data.hex()}")
    print(f"Text: {data}")
except Exception as e:
    print(e)

import os
import glob

directory = r"e:\duanshiping\camera_tool\backend\temp_frames"
files = glob.glob(os.path.join(directory, "*.png"))
print(f"Found {len(files)} files to rename.")

for f in files:
    base = os.path.splitext(f)[0]
    new_name = base + ".jpg"
    try:
        if os.path.exists(new_name):
            os.remove(new_name)
        os.rename(f, new_name)
    except Exception as e:
        print(f"Error renaming {f}: {e}")

print("Renaming complete.")

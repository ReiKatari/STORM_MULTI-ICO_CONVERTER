import os
from PIL import Image

def verify_append_order():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_append_64first.ico"
    
    if not os.path.exists(source_img):
        print(f"Error: {source_img} not found.")
        return

    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            
            # Prepare all frames
            s64 = img.resize((64, 64), Image.Resampling.LANCZOS)
            s256 = img.resize((256, 256), Image.Resampling.LANCZOS)
            s128 = img.resize((128, 128), Image.Resampling.LANCZOS)
            s48 = img.resize((48, 48), Image.Resampling.LANCZOS)
            s32 = img.resize((32, 32), Image.Resampling.LANCZOS)
            s16 = img.resize((16, 16), Image.Resampling.LANCZOS)
            
            # Save: 64 is BASE, others are APPENDED
            others = [s256, s128, s48, s32, s16]
            s64.save(out_path, format='ICO', append_images=others)
            print(f"Created {out_path}")
            
    except Exception as e:
        print(f"Creation failed: {e}")

    # Check frames
    try:
        with Image.open(out_path) as img:
            print(f"Main size (index 0): {img.size}")
            
            # Pillow doesn't make it easy to see the directory order directly in simple .open()
            # But the 'sizes' in .info might be ordered? 
            # Let's count frames if possible (ICO often handled as multi-frame)
            frames = 0
            try:
                while True:
                    print(f"Frame {frames} size: {img.size}")
                    frames += 1
                    img.seek(frames)
            except EOFError:
                pass
            print(f"Total frames: {frames}")
            
            if img.size == (64, 64):
                # We need to seek back to 0 to verify it started with 64
                img.seek(0)
                if img.size == (64, 64):
                    print("SUCCESS: 64x64 is at frame 0.")
            
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    verify_append_order()

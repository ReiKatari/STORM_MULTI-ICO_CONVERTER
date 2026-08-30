import os
from PIL import Image

def create_test_ico_ascending_fixed():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_ascending_fixed.ico"
    
    if not os.path.exists(source_img):
        print(f"Error: {source_img} not found.")
        return

    # Ascending
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)]
    
    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            resized_images = []
            for size in ico_sizes:
                resized_images.append(img.resize(size, Image.Resampling.LANCZOS))
            
            # FIX: Pass sizes
            resized_images[0].save(out_path, format='ICO', sizes=[(i.width, i.height) for i in resized_images], append_images=resized_images[1:])
            print(f"Created {out_path}")
            
    except Exception as e:
        print(f"Creation failed: {e}")

def verify_ico_ascending_fixed():
    out_path = "test_ascending_fixed.ico"
    if not os.path.exists(out_path):
        print("Output file not found.")
        return

    try:
        with Image.open(out_path) as img:
            print(f"ICO info: {img.info}")
            print(f"ICO size (default/first): {img.size}")
            
            # Check if 16x16 is first (Ascending)
            if img.size == (16, 16):
                 print("SUCCESS: 16x16 is first.")
            else:
                 print(f"FAILURE: Unexpected first size {img.size}.")

            if 'sizes' in img.info:
                print(f"Sizes in ICO: {img.info['sizes']}")
                if (256, 256) in img.info['sizes']:
                    print("SUCCESS: 256x256 layer exists.")
                else:
                    print("FAILURE: 256x256 layer MISSING.")

    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    create_test_ico_ascending_fixed()
    verify_ico_ascending_fixed()

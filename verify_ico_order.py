import os
from PIL import Image

# Mocking the logic from the app
def create_test_ico():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_output.ico"
    
    if not os.path.exists(source_img):
        print(f"Error: {source_img} not found.")
        return

    # The NEW order
    ico_sizes = [(64, 64), (16, 16), (32, 32), (48, 48), (128, 128), (256, 256)]
    
    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            resized_images = []
            for size in ico_sizes:
                resized_images.append(img.resize(size, Image.Resampling.LANCZOS))
            
            # Save using the first image as base
            resized_images[0].save(out_path, format='ICO', sizes=[(i.width, i.height) for i in resized_images], append_images=resized_images[1:])
            print(f"Created {out_path}")
            
    except Exception as e:
        print(f"Creation failed: {e}")

def verify_ico():
    out_path = "test_output.ico"
    if not os.path.exists(out_path):
        print("Output file not found.")
        return

    try:
        with Image.open(out_path) as img:
            print(f"ICO info: {img.info}")
            print(f"ICO size (default/first): {img.size}")
            
            # Check if the default loaded size is 64x64
            if img.size == (64, 64):
                print("SUCCESS: Default icon size is 64x64.")
            else:
                print(f"FAILURE: Default icon size is {img.size}, expected (64, 64).")
                
            # List all sizes (Pillow's ICO plugin might not easily expose the directory order directly in .info['sizes'] in a specific way, but usually it does).
            # ACTUALLY: Pillow's ICO plugin puts the sizes in `info['sizes']`.
            if 'sizes' in img.info:
                print(f"All sizes in ICO: {img.info['sizes']}")
                
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    create_test_ico()
    verify_ico()

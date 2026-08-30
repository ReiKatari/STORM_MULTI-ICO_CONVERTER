import os
from PIL import Image

def create_test_ico_mixed():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_mixed.ico"
    
    if not os.path.exists(source_img):
        print(f"Error: {source_img} not found.")
        return

    # Strategy: Base is 256 (to ensure file validity/Pillow happiness). 
    # Appended are 16...64.
    
    base_size = (256, 256)
    other_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    
    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            
            base_img = img.resize(base_size, Image.Resampling.LANCZOS)
            other_imgs = [img.resize(s, Image.Resampling.LANCZOS) for s in other_sizes]
            
            # Save: Base + Others
            base_img.save(out_path, format='ICO', append_images=other_imgs)
            print(f"Created {out_path}")
            
    except Exception as e:
        print(f"Creation failed: {e}")

def verify_ico_mixed():
    out_path = "test_mixed.ico"
    if not os.path.exists(out_path):
        print("Output file not found.")
        return

    try:
        with Image.open(out_path) as img:
            print(f"ICO info: {img.info}")
            print(f"ICO size (default/first): {img.size}")
            
            if img.size == (256, 256):
                 print("SUCCESS: 256x256 is first.")
            else:
                 print(f"FAILURE: First size is {img.size}.")

            if 'sizes' in img.info:
                print(f"Sizes in ICO: {img.info['sizes']}")
                if (256, 256) in img.info['sizes'] and (16, 16) in img.info['sizes']:
                    print("SUCCESS: All layers present.")
                else:
                    print("FAILURE: Layers missing.")

    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    create_test_ico_mixed()
    verify_ico_mixed()

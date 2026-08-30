import os
from PIL import Image

def verify_64base_with_256size():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_64base_256size.ico"
    
    if not os.path.exists(source_img):
        return

    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            # Create a 64x64 base
            base_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
            
            # Request sizes including 256
            sizes = [(64, 64), (256, 256), (48, 48), (32, 32), (16, 16)]
            
            base_64.save(out_path, format='ICO', sizes=sizes)
            print(f"Created {out_path}")
            
        with Image.open(out_path) as result:
            print(f"Index 0 size: {result.size}")
            if 'sizes' in result.info:
                print(f"All sizes: {result.info['sizes']}")
                if (256, 256) in result.info['sizes']:
                    print("SUCCESS: 256x256 preserved!")
                else:
                    print("FAILURE: 256x256 dropped.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_64base_with_256size()

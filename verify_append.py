import os
from PIL import Image

def verify_append():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_append_final.ico"
    
    if not os.path.exists(source_img):
        return

    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            s64 = img.resize((64, 64), Image.Resampling.LANCZOS)
            s256 = img.resize((256, 256), Image.Resampling.LANCZOS)
            others = [s256, img.resize((16, 16), Image.Resampling.LANCZOS)]
            
            # Save
            s64.save(out_path, format='ICO', append_images=others)
            
        with Image.open(out_path) as result:
            print(f"Index 0 size: {result.size}")
            if 'sizes' in result.info:
                print(f"All sizes: {result.info['sizes']}")
            else:
                print("No sizes info.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_append()

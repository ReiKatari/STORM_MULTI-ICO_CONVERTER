import os
from PIL import Image

def create_test_ico_pillow_correct():
    source_img = "stormmultiicoconverter.jpg"
    out_path = "test_pillow_correct.ico"
    
    if not os.path.exists(source_img):
        print(f"Error: {source_img} not found.")
        return

    # Try Ascending again but verify logic
    # ICO plugin in Pillow saves the image provided in 'fp' (the first one) PLUS 'append_images'.
    # If the first image is 16x16, the ICO header might be set to that?
    # Actually, previous attempts with 256 first WORKED (all layers present).
    # Why does 16 first fail?
    # Maybe because the main image object dominates the saving process.
    
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)]
    
    try:
        with Image.open(source_img) as img:
            img = img.convert("RGBA")
            resized_images = []
            for size in ico_sizes:
                resized_images.append(img.resize(size, Image.Resampling.LANCZOS))
            
            # ATTEMPT: Pass ALL images in append_images, and save a Dummy? NO.
            # ATTEMPT: Save the 256x256 one as the 'base', but append the others (swapping order in memory only)?
            # If I want 16x16 to be FIRST in the file, I must call save on the 16x16 image.
            # Is there a bug in Pillow regarding appending larger images to a smaller base?
            
            base = resized_images[0] # 16x16
            others = resized_images[1:] # 32...256
            
            # Explicitly checking sizes
            print(f"Base: {base.size}")
            print(f"Others: {[i.size for i in others]}")
            
            base.save(out_path, format='ICO', append_images=others)
            print(f"Created {out_path}")
            
    except Exception as e:
        print(f"Creation failed: {e}")

def verify_ico_pillow_correct():
    out_path = "test_pillow_correct.ico"
    if not os.path.exists(out_path):
        print("Output file not found.")
        return

    try:
        with Image.open(out_path) as img:
            print(f"ICO info: {img.info}")
            if 'sizes' in img.info:
                 print(f"Sizes in ICO: {img.info['sizes']}")
            else:
                 print("No sizes info found (Single layer?)")

    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    create_test_ico_pillow_correct()
    verify_ico_pillow_correct()

import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/base.png").convert("RGBA")
    arr = np.array(img)
    
    # Restrict to face region Y in [100, 300], X in [500, 720]
    face_region = arr[100:300, 500:720]
    h, w = face_region.shape[:2]
    
    # We want to identify the eye pixels in base.png.
    # Eye pixels in a skin face are usually:
    # - Dark lines (eyelashes, pupils)
    # - Eye colors (blue/green/brown)
    # - Sclera (white of the eye, but wait - background is also white!)
    # Let's search for pixels in face_region that do NOT match skin or hair.
    # Skin: R > 200, 130 < G < 210, 100 < B < 185
    # Hair: R > 200, G > 170, B < 120
    # Background (white): R > 240, G > 240, B > 240
    
    skin_mask = (face_region[:,:,0] > 200) & (face_region[:,:,1] > 130) & (face_region[:,:,1] < 210) & (face_region[:,:,2] > 100) & (face_region[:,:,2] < 185)
    hair_mask = (face_region[:,:,0] > 200) & (face_region[:,:,1] > 170) & (face_region[:,:,2] < 120)
    bg_mask = (face_region[:,:,0] > 240) & (face_region[:,:,1] > 240) & (face_region[:,:,2] > 240)
    
    # Non-skin, non-hair, non-bg pixels
    eye_mask = (~skin_mask) & (~hair_mask) & (~bg_mask)
    
    eye_y, eye_x = np.where(eye_mask)
    if len(eye_y) > 0:
        actual_y = eye_y + 100
        actual_x = eye_x + 500
        print("Detected eye pixels in tmp/base.png:")
        print(f"Y bounds: {actual_y.min()} to {actual_y.max()} (Height: {actual_y.max() - actual_y.min() + 1})")
        print(f"X bounds: {actual_x.min()} to {actual_x.max()} (Width: {actual_x.max() - actual_x.min() + 1})")
        print(f"Center of eyes: Y={int(np.mean(actual_y))}, X={int(np.mean(actual_x))}")
        
        # Crop eye area and save to inspect
        img.crop((actual_x.min() - 10, actual_y.min() - 10, actual_x.max() + 10, actual_y.max() + 10)).save("scratch/eyes_detected.png")
        print("Saved scratch/eyes_detected.png!")
    else:
        print("No eye pixels detected using skin/hair thresholds!")

if __name__ == "__main__":
    main()

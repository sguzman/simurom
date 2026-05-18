import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/eyes-open.png").convert("RGBA")
    arr = np.array(img)
    
    # Non-white pixels
    non_white = np.argwhere((arr[:,:,0] <= 240) | (arr[:,:,1] <= 240) | (arr[:,:,2] <= 240))
    
    if len(non_white) > 0:
        y_min, x_min = non_white.min(axis=0)[:2]
        y_max, x_max = non_white.max(axis=0)[:2]
        y_center = (y_min + y_max) / 2
        x_center = (x_min + x_max) / 2
        print("eyes-open.png:")
        print(f"Y bounds: {y_min} to {y_max} (Center Y: {y_center})")
        print(f"X bounds: {x_min} to {x_max} (Center X: {x_center})")
        
        # Let's check left eye and right eye centers separately
        # Left eye: X < 627 (the middle of the canvas)
        left_eye_pixels = non_white[non_white[:, 1] < 627]
        right_eye_pixels = non_white[non_white[:, 1] >= 627]
        
        if len(left_eye_pixels) > 0:
            ly_min, lx_min = left_eye_pixels.min(axis=0)[:2]
            ly_max, lx_max = left_eye_pixels.max(axis=0)[:2]
            print(f"  Left Eye: Y={ly_min}:{ly_max} (Center: {(ly_min+ly_max)/2}), X={lx_min}:{lx_max} (Center: {(lx_min+lx_max)/2})")
            
        if len(right_eye_pixels) > 0:
            ry_min, rx_min = right_eye_pixels.min(axis=0)[:2]
            ry_max, rx_max = right_eye_pixels.max(axis=0)[:2]
            print(f"  Right Eye: Y={ry_min}:{ry_max} (Center: {(ry_min+ry_max)/2}), X={rx_min}:{rx_max} (Center: {(rx_min+rx_max)/2})")
            
        # Overall center of the two eyes
        print(f"  Overall Center: Y={y_center}, X={x_center}")
        
    else:
        print("No non-white pixels in eyes-open.png")

if __name__ == "__main__":
    main()

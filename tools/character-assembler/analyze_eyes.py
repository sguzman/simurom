import numpy as np
from PIL import Image

def main():
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    arr_e = np.array(img_e)
    h, w = arr_e.shape[:2]
    
    opaque_y, opaque_x = np.where(arr_e[:,:,3] > 0)
    if len(opaque_y) == 0:
        print("No opaque eye pixels!")
        return
        
    print("Eyes opaque bounds:")
    print("Y:", opaque_y.min(), "to", opaque_y.max())
    print("X:", opaque_x.min(), "to", opaque_x.max())
    
    # Let's find the left and right eyes based on X coordinate
    mid_x = (opaque_x.min() + opaque_x.max()) // 2
    left_eye_y, left_eye_x = np.where((arr_e[:,:,3] > 0) & (np.indices((h, w))[1] <= mid_x))
    right_eye_y, right_eye_x = np.where((arr_e[:,:,3] > 0) & (np.indices((h, w))[1] > mid_x))
    
    print("Left eye bounds:")
    print(f"  Y: {left_eye_y.min()} to {left_eye_y.max()}")
    print(f"  X: {left_eye_x.min()} to {left_eye_x.max()}")
    print(f"  Size: {left_eye_x.max() - left_eye_x.min() + 1}x{left_eye_y.max() - left_eye_y.min() + 1}")
    
    print("Right eye bounds:")
    print(f"  Y: {right_eye_y.min()} to {right_eye_y.max()}")
    print(f"  X: {right_eye_x.min()} to {right_eye_x.max()}")
    print(f"  Size: {right_eye_x.max() - right_eye_x.min() + 1}x{right_eye_y.max() - right_eye_y.min() + 1}")

if __name__ == "__main__":
    main()

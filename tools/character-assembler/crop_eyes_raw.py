from PIL import Image
import numpy as np
import os

def main():
    frames = [
        "assets/mini_game/images/blonde_eyes_open.png",
        "assets/mini_game/images/blonde_eyes_partial1.png",
        "assets/mini_game/images/blonde_eyes_partial2.png",
        "assets/mini_game/images/blonde_eyes_partial3.png",
        "assets/mini_game/images/blonde_eyes_closed.png"
    ]
    
    # Check if all files exist
    for f in frames:
        if not os.path.exists(f):
            print(f"File not found: {f}")
            return
            
    # Find the union of bounding boxes of all 5 frames
    min_x, min_y = 9999, 9999
    max_x, max_y = 0, 0
    
    for f in frames:
        img = Image.open(f).convert("RGBA")
        arr = np.array(img)
        alpha = arr[:, :, 3]
        y_indices, x_indices = np.where(alpha > 0)
        if len(x_indices) > 0:
            min_x = min(min_x, np.min(x_indices))
            max_x = max(max_x, np.max(x_indices))
            min_y = min(min_y, np.min(y_indices))
            max_y = max(max_y, np.max(y_indices))
            
    print(f"Union BBox of raw eyes: X [{min_x}, {max_x}], Y [{min_y}, {max_y}]")
    print(f"Dimensions: {max_x - min_x + 1} x {max_y - min_y + 1}")

if __name__ == "__main__":
    main()

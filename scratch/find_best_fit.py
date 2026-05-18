import os
import numpy as np
from PIL import Image

def main():
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Bounding box of eyes
    # Y: 482 to 717 (height 235)
    # X: 278 to 973 (width 695)
    eyes_crop = img_e.crop((278, 482, 973, 717))
    
    # We want to test different scales and positions
    # Scales: 0.16, 0.18, 0.20, 0.22
    # Y-centers: 150, 160, 170, 180, 190
    os.makedirs("scratch/fit", exist_ok=True)
    
    for scale in [0.16, 0.18, 0.20, 0.22]:
        w_new = int(695 * scale)
        h_new = int(235 * scale)
        eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
        
        for y_center in [150, 160, 170, 180, 190]:
            # Center the eyes horizontally at X = 612
            # Left coordinate = 612 - w_new / 2
            # Top coordinate = y_center - h_new / 2
            x_left = int(612 - w_new / 2)
            y_top = int(y_center - h_new / 2)
            
            # Composite
            temp = img_b.copy()
            temp.paste(eyes_resized, (x_left, y_top), eyes_resized)
            
            # Crop to head region to view closely
            head = temp.crop((450, 50, 750, 350))
            head.save(f"scratch/fit/scale_{scale:.2f}_y_{y_center}.png")
            
    print("Generated test fit crops in scratch/fit/!")

if __name__ == "__main__":
    main()

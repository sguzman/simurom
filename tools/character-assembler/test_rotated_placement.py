import numpy as np
from PIL import Image

def main():
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Bounding box of eyes in blonde_eyes_open.png:
    # Y: 482 to 717 (height 235)
    # X: 278 to 973 (width 695)
    eyes_crop = img_e.crop((278, 482, 973, 717))
    
    # We found distance ratio is 0.190
    scale = 0.190
    w_new = int(695 * scale)
    h_new = int(235 * scale)
    
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    
    # Let's rotate the resized eyes image by 10.56 degrees (counter-clockwise is positive in PIL.Image.rotate)
    # Since we want to tilt it so left is lower and right is higher, wait:
    # Right eye is higher than left eye (Y=247.18 < Y=263.40).
    # In screen coordinates, smaller Y is HIGHER. So the right side is higher.
    # A standard horizontal line has left and right at the same Y.
    # If we rotate it counter-clockwise (positive angle), the right side goes UP (smaller Y).
    # So we rotate by +10.56 degrees! Let's do that!
    eyes_rotated = eyes_resized.rotate(10.56, Image.Resampling.BICUBIC, expand=True)
    
    # Let's find the new size and paste it centered at X = 611.75, Y = 255.29
    w_rot, h_rot = eyes_rotated.size
    
    x_left = int(611.75 - w_rot / 2)
    y_top = int(255.29 - h_rot / 2)
    
    # Paste onto base
    composite = img_b.copy()
    composite.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
    
    composite.save("scratch/test_rotated_placement.png")
    head = composite.crop((450, 50, 750, 380))
    head.save("scratch/test_rotated_head.png")
    
    print(f"Pasted rotated eyes at scale={scale}, top_left=({x_left}, {y_top})")
    print("Saved preview to scratch/test_rotated_placement.png and scratch/test_rotated_head.png")

if __name__ == "__main__":
    main()

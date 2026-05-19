from PIL import Image

def main():
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Bounding box of eyes in blonde_eyes_open.png:
    # Y: 482 to 717 (height 235)
    # X: 278 to 973 (width 695)
    eyes_crop = img_e.crop((278, 482, 973, 717))
    
    # We found scale 0.1813 is the perfect scale!
    scale = 0.1813
    w_new = int(695 * scale)
    h_new = int(235 * scale)
    
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    
    # Center horizontally at X = 612, vertically at Y = 259
    x_left = int(612 - w_new / 2)
    y_top = int(259 - h_new / 2)
    
    # Paste onto base
    composite = img_b.copy()
    composite.paste(eyes_resized, (x_left, y_top), eyes_resized)
    
    # Save preview of the full image
    composite.save("scratch/test_eye_placement.png")
    
    # Save crop of the head
    head = composite.crop((450, 50, 750, 380))
    head.save("scratch/test_head_placement.png")
    print(f"Pasted eyes at scale={scale}, top_left=({x_left}, {y_top})")
    print("Saved preview to scratch/test_eye_placement.png and scratch/test_head_placement.png")

if __name__ == "__main__":
    main()

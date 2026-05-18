import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    return arr

def main():
    base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    base_orig_raw = Image.open("tmp/base.png").convert("RGBA")
    hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    base_arr = simple_key(base_raw)
    base_orig_arr = simple_key(base_orig_raw)
    
    s = 0.57
    new_w = int(round(hair_raw.width * s))
    new_h = int(round(hair_raw.height * s))
    scaled_hair = hair_raw.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    # Grid search for left/top in pixels
    # Since raw hair width is 791 and scaled is ~451, we want it to cover x from 421 to 872.
    # So the left edge should be around 421.
    # Since raw hair height is 932 and scaled is ~531, let's see where the top should be.
    # In base.png, the hair starts at y=29.
    # So top edge should be around 29.
    
    best_err = float('inf')
    best_left = 0
    best_top = 0
    
    # Grid search around left=410, top=42
    for left in range(350, 450):
        for top in range(10, 80):
            canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
            canvas.paste(scaled_hair, (left, top), scaled_hair)
            canvas_arr = np.array(canvas)
            
            # Error over the entire canvas (excluding transparent pixels in canvas)
            mask = canvas_arr[:, :, 3] > 0
            err = np.mean(np.abs(canvas_arr[mask].astype(float) - base_orig_arr[mask].astype(float)))
            if err < best_err:
                best_err = err
                best_left = left
                best_top = top
                
    print(f"Best Left: {best_left}, Best Top: {best_top}")
    print(f"Best Error: {best_err:.4f}")
    
    # Save composite for visual inspection
    comp = Image.fromarray(base_arr)
    comp.paste(scaled_hair, (best_left, best_top), scaled_hair)
    comp.save("scratch/test_hair_0.57.png")
    
    # Calculate TOML offset
    # placed_cx = left + new_w / 2.0
    # placed_cy = top + new_h / 2.0
    placed_cx = best_left + new_w / 2.0
    placed_cy = best_top + new_h / 2.0
    toml_x = placed_cx - 627.0
    toml_y = 627.0 - placed_cy
    print(f"TOML scale: 0.57")
    print(f"TOML offset: x = {toml_x:.1f}, y = {toml_y:.1f}")

if __name__ == "__main__":
    main()

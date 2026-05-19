import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask] = 0
    return arr

def main():
    base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    base_orig_raw = Image.open("tmp/base.png").convert("RGBA")
    hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    base_orig_arr = simple_key(base_orig_raw)
    
    # We want to find the scale `s` and top-left `(left, top)` for `hair_raw`
    # so that when placed on top of `base-no-hair-eyes.png`, it matches `base_orig_raw`.
    # Let's perform a coarse-to-fine search using the full 1254x1254 image absolute difference.
    
    best_err = float('inf')
    best_s = 0.0
    best_left = 0
    best_top = 0
    
    # Coarse search: s from 0.4 to 0.7, left from 200 to 500, top from -50 to 200
    # Let's do scale first:
    # We know the original hair has w=452, h=1175.
    # But wait, in the original base, is the hair scaled uniformly?
    # Let's check: if the hair in base_orig has a width of 452 and height of 1175,
    # but raw hair has w=791 and h=932, then maybe the hair in base_orig is NOT scaled uniformly,
    # or the raw hair image has extra wide margins that were cropped out?
    # Let's check if the hair in tmp/hair.png matches the visual shape of the hair in base.png.
    # Yes! In base.png, the hair has a long tuft at the top and twin tails.
    # Let's find the scale by matching the top tuft and side shapes.
    
    # Let's do a fast grid search for s, left, top:
    # To make it fast, we can resize images to 128x128 for coarse search!
    # No, we can just do a multi-resolution search!
    # Let's do a quick python search with step size 5 for pixels and 0.01 for scale.
    
    scales = np.linspace(0.40, 0.70, 31)
    
    # Let's estimate where the hair center is in base_orig.
    # The head center in base-no-hair-eyes is around x = 627, y = 200.
    # So the hair should be centered around x = 627, and top of the head is at y = 106.
    # So top of hair should be around y = 29.
    
    for s in scales:
        new_w = int(round(hair_raw.width * s))
        new_h = int(round(hair_raw.height * s))
        if new_w <= 0 or new_h <= 0:
            continue
        scaled_hair = hair_raw.resize((new_w, new_h), Image.Resampling.BILINEAR)
        scaled_arr = np.array(scaled_hair)
        
        # Bounding box of scaled hair:
        ys, xs = np.where(scaled_arr[:, :, 3] > 0)
        if len(ys) == 0:
            continue
            
        # We want the top of the scaled hair's active pixels to align near y = 29.
        # And the horizontal center of the active pixels to align near x = 627.
        hair_act_top = ys.min()
        hair_act_cx = xs.min() + (xs.max() - xs.min()) / 2.0
        
        # So:
        # left + hair_act_cx = 627  => left = 627 - hair_act_cx
        # top + hair_act_top = 29   => top = 29 - hair_act_top
        
        est_left = int(round(627.0 - hair_act_cx))
        est_top = int(round(29.0 - hair_act_top))
        
        # Search around this estimate
        for dx in range(-30, 31, 2):
            for dy in range(-30, 31, 2):
                left = est_left + dx
                top = est_top + dy
                
                # Fast check using a bounding box of the head/hair region to save time!
                # We only need to check the region x in [300, 950], y in [0, 600]
                # Because the hair is mostly in the upper half!
                canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
                canvas.paste(scaled_hair, (left, top), scaled_hair)
                canvas_arr = np.array(canvas)
                
                # Compute absolute difference in the upper half of the image
                diff = np.mean(np.abs(canvas_arr[0:600, 300:950].astype(float) - base_orig_arr[0:600, 300:950].astype(float)))
                if diff < best_err:
                    best_err = diff
                    best_s = s
                    best_left = left
                    best_top = top
                    
    print(f"Optimal scale s: {best_s:.4f}")
    print(f"Optimal left: {best_left}, top: {best_top}")
    print(f"Minimum Error: {best_err:.4f}")
    
    # Generate and save the perfect composite
    scaled_hair = hair_raw.resize((int(round(hair_raw.width * best_s)), int(round(hair_raw.height * best_s))), Image.Resampling.BILINEAR)
    comp = base_raw.copy()
    comp.paste(scaled_hair, (best_left, best_top), scaled_hair)
    comp.save("scratch/perfect_hair_fit.png")
    
    # Compute Bevy/TOML offsets
    new_w = int(round(hair_raw.width * best_s))
    new_h = int(round(hair_raw.height * best_s))
    placed_cx = best_left + new_w / 2.0
    placed_cy = best_top + new_h / 2.0
    toml_x = placed_cx - 627.0
    toml_y = 627.0 - placed_cy
    print(f"Calculated TOML: scale = {best_s:.4f}, offset = {{ x = {toml_x:.2f}, y = {toml_y:.2f} }}")

if __name__ == "__main__":
    main()

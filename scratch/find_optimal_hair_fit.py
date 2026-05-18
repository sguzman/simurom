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
    hair_arr = simple_key(hair_raw)
    
    # We want to find the scale and offset (ox, oy) for the hair so that when placed,
    # it matches the hair in base_orig.
    # Specifically, the hair in base_orig is present where base_orig has alpha > 0 but base has alpha == 0.
    # Let's find the bounding box of that difference region in base_orig.
    diff_mask = (base_orig_arr[:, :, 3] > 0) & (base_arr[:, :, 3] == 0)
    ys, xs = np.where(diff_mask)
    if len(ys) == 0:
        print("No difference found!")
        return
        
    diff_ymin, diff_ymax = ys.min(), ys.max()
    diff_xmin, diff_xmax = xs.min(), xs.max()
    diff_w = diff_xmax - diff_xmin + 1
    diff_h = diff_ymax - diff_ymin + 1
    
    print(f"Original baked hair bbox: xmin={diff_xmin}, ymin={diff_ymin}, w={diff_w}, h={diff_h}")
    
    # BBox of raw hair:
    hair_ys, hair_xs = np.where(hair_arr[:, :, 3] > 0)
    hair_ymin, hair_ymax = hair_ys.min(), hair_ys.max()
    hair_xmin, hair_xmax = hair_xs.min(), hair_xs.max()
    hair_w = hair_xmax - hair_xmin + 1
    hair_h = hair_ymax - hair_ymin + 1
    
    print(f"Raw hair bbox: xmin={hair_xmin}, ymin={hair_ymin}, w={hair_w}, h={hair_h}")
    
    # Scale estimates
    scale_w = diff_w / hair_w
    scale_h = diff_h / hair_h
    print(f"Estimated scale from width: {scale_w:.4f}")
    print(f"Estimated scale from height: {scale_h:.4f}")
    
    # Let's find the best fit scale by grid search
    best_err = float('inf')
    best_scale = 0.0
    best_ox = 0.0
    best_oy = 0.0
    
    # The center of the raw hair bbox is:
    hair_cx = hair_xmin + hair_w / 2.0
    hair_cy = hair_ymin + hair_h / 2.0
    
    # The center of the diff bbox is:
    diff_cx = diff_xmin + diff_w / 2.0
    diff_cy = diff_ymin + diff_h / 2.0
    
    # Grid search around the estimated scale (~0.57)
    for s in np.linspace(0.53, 0.61, 41):
        # Scale raw hair
        new_w = int(round(hair_raw.width * s))
        new_h = int(round(hair_raw.height * s))
        if new_w <= 0 or new_h <= 0:
            continue
            
        scaled_hair = hair_raw.resize((new_w, new_h), Image.Resampling.BILINEAR)
        scaled_arr = np.array(scaled_hair)
        scaled_mask = scaled_arr[:, :, 3] > 0
        s_ys, s_xs = np.where(scaled_mask)
        if len(s_ys) == 0:
            continue
        s_w = s_xs.max() - s_xs.min() + 1
        s_h = s_ys.max() - s_ys.min() + 1
        s_cx = s_xs.min() + s_w / 2.0
        s_cy = s_ys.min() + s_h / 2.0
        
        # Center alignment offset
        base_ox = diff_cx - s_cx
        base_oy = diff_cy - s_cy
        
        # Search for fine-tuning offsets
        for dx in range(-8, 9, 2):
            for dy in range(-8, 9, 2):
                ox = base_ox + dx
                oy = base_oy + dy
                
                # Check alignment error
                # We can place scaled_hair on a canvas of 1254x1254 at the offset
                test_canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
                # Pillow paste takes top-left corner
                # We want the center of scaled_hair to land at (s_cx + ox, s_cy + oy)
                # No, wait, top-left is (diff_cx - s_cx)
                left = int(round((1254 - new_w) / 2.0 + (ox - (1254 - new_w)/2.0))) # Wait, simpler:
                # The top-left of the original raw hair image was (0,0).
                # After resizing to new_w, new_h:
                # We want to paste it at `left`, `top` on the 1254x1254 canvas.
                # Let's align centers:
                # raw hair center was (hair_raw.width / 2.0, hair_raw.height / 2.0)
                # scaled hair center is (new_w / 2.0, new_h / 2.0)
                # In Python, we want to paste scaled_hair so its center matches diff_cx, diff_cy (with fine-tuning)
                left = int(round(diff_cx - (new_w / 2.0) + dx))
                top = int(round(diff_cy - (new_h / 2.0) + dy))
                
                # Draw on canvas
                canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
                canvas.paste(scaled_hair, (left, top), scaled_hair)
                canvas_arr = np.array(canvas)
                
                # Compare canvas_arr with base_orig_arr in the hair region (where diff_mask is True)
                # We can compute the difference in RGB channels where both have alpha or where diff_mask is true
                err = np.mean(np.abs(canvas_arr[diff_mask].astype(float) - base_orig_arr[diff_mask].astype(float)))
                if err < best_err:
                    best_err = err
                    best_scale = s
                    best_left = left
                    best_top = top
                    
    print(f"Best Scale: {best_scale:.4f}")
    print(f"Best Left: {best_left}, Best Top: {best_top}")
    print(f"Best Error: {best_err:.4f}")
    
    # Convert best_left and best_top to TOML offset (x, y)
    # In python, center of canvas is (627, 627)
    # In Bevy/TOML, center is (0,0), and:
    # offset_x = (center of placed hair) - 627
    # offset_y = 627 - (center of placed hair)
    # Let's compute this:
    placed_cx = best_left + (int(round(hair_raw.width * best_scale)) / 2.0)
    placed_cy = best_top + (int(round(hair_raw.height * best_scale)) / 2.0)
    
    toml_x = placed_cx - 627.0
    toml_y = 627.0 - placed_cy
    print(f"Calculated TOML offset: x = {toml_x:.1f}, y = {toml_y:.1f}")

if __name__ == "__main__":
    main()

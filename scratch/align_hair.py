import numpy as np
from PIL import Image

def main():
    # Load images
    old_base_raw = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    new_base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    new_hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    # Key out white backgrounds (R,G,B > 240)
    def simple_key(img):
        arr = np.array(img)
        mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
        arr[mask, 3] = 0
        return arr
        
    old_arr = np.array(old_base_raw) # already transparent in assets
    new_base_arr = simple_key(new_base_raw)
    new_hair_arr = simple_key(new_hair_raw)
    
    # Ground truth hair: pixels in old_base that are NOT in new_base
    # Since new_base has alpha=0 where there was no body, let's find where old_base has hair but new_base has alpha=0
    gt_hair_mask = (old_arr[:, :, 3] > 0) & (new_base_arr[:, :, 3] == 0)
    
    # We want to find the offset (dx, dy) and scale (s) of new_hair that best matches gt_hair_mask
    # Let's perform a grid search over:
    # - dx: from -100 to 100
    # - dy: from -200 to 100
    # - scale: from 0.8 to 1.2
    
    # To do it fast, let's downsample or do coarse-to-fine search
    # Let's first extract the mask of the new hair
    hair_mask = new_hair_arr[:, :, 3] > 0
    
    best_score = -1e9
    best_params = (0, 0, 1.0)
    
    # Coarse search
    print("Starting coarse alignment search...")
    for s in np.linspace(0.8, 1.2, 9):
        # Resize hair mask
        h_scaled = int(hair_mask.shape[0] * s)
        w_scaled = int(hair_mask.shape[1] * s)
        if h_scaled == 0 or w_scaled == 0:
            continue
        scaled_mask = np.array(Image.fromarray(hair_mask).resize((w_scaled, h_scaled), Image.NEAREST))
        
        for dy in range(-200, 100, 10):
            for dx in range(-150, 50, 10):
                # Map scaled mask into a 1254x1254 canvas centered and shifted
                canvas = np.zeros((1254, 1254), dtype=bool)
                
                # Center-based alignment
                target_cx = 1254 / 2.0
                target_cy = 1254 / 2.0
                src_cx = w_scaled / 2.0
                src_cy = h_scaled / 2.0
                
                # We want to shift by dx, dy
                # ty = round(sy - src_cy + target_cy + dy)
                # tx = round(sx - src_cx + target_cx + dx)
                
                # Calculate bounding box in canvas
                c_min_y = int(round(target_cy - src_cy + dy))
                c_min_x = int(round(target_cx - src_cx + dx))
                
                c_max_y = c_min_y + h_scaled
                c_max_x = c_min_x + w_scaled
                
                # Clip to canvas dimensions
                y_start = max(0, c_min_y)
                y_end = min(1254, c_max_y)
                x_start = max(0, c_min_x)
                x_end = min(1254, c_max_x)
                
                h_start = y_start - c_min_y
                h_end = y_end - c_min_y
                w_start = x_start - c_min_x
                w_end = x_end - c_min_x
                
                if y_end > y_start and x_end > x_start:
                    canvas[y_start:y_end, x_start:x_end] = scaled_mask[h_start:h_end, w_start:w_end]
                    
                # Score: intersection over union or simple overlap
                intersection = np.sum(canvas & gt_hair_mask)
                union = np.sum(canvas | gt_hair_mask)
                score = intersection / (union + 1)
                
                if score > best_score:
                    best_score = score
                    best_params = (dx, dy, s)
                    print(f"New best coarse score: {best_score:.4f} at dx={dx}, dy={dy}, s={s:.3f}")
                    
    # Fine search around best coarse params
    print("\nStarting fine alignment search...")
    coarse_dx, coarse_dy, coarse_s = best_params
    best_score = -1e9
    for s in np.linspace(coarse_s - 0.03, coarse_s + 0.03, 13):
        h_scaled = int(hair_mask.shape[0] * s)
        w_scaled = int(hair_mask.shape[1] * s)
        scaled_mask = np.array(Image.fromarray(hair_mask).resize((w_scaled, h_scaled), Image.NEAREST))
        
        for dy in range(coarse_dy - 12, coarse_dy + 12):
            for dx in range(coarse_dx - 12, coarse_dx + 12):
                canvas = np.zeros((1254, 1254), dtype=bool)
                target_cx = 1254 / 2.0
                target_cy = 1254 / 2.0
                src_cx = w_scaled / 2.0
                src_cy = h_scaled / 2.0
                
                c_min_y = int(round(target_cy - src_cy + dy))
                c_min_x = int(round(target_cx - src_cx + dx))
                
                c_max_y = c_min_y + h_scaled
                c_max_x = c_min_x + w_scaled
                
                y_start = max(0, c_min_y)
                y_end = min(1254, c_max_y)
                x_start = max(0, c_min_x)
                x_end = min(1254, c_max_x)
                
                h_start = y_start - c_min_y
                h_end = y_end - c_min_y
                w_start = x_start - c_min_x
                w_end = x_end - c_min_x
                
                if y_end > y_start and x_end > x_start:
                    canvas[y_start:y_end, x_start:x_end] = scaled_mask[h_start:h_end, w_start:w_end]
                    
                intersection = np.sum(canvas & gt_hair_mask)
                union = np.sum(canvas | gt_hair_mask)
                score = intersection / (union + 1)
                
                if score > best_score:
                    best_score = score
                    best_params = (dx, dy, s)
                    print(f"New best fine score: {best_score:.4f} at dx={dx}, dy={dy}, s={s:.4f}")
                    
    print(f"\nFinal optimal alignment: dx={best_params[0]}, dy={best_params[1]}, scale={best_params[2]:.4f}")

if __name__ == "__main__":
    main()

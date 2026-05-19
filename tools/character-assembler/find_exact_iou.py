import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    return arr

def main():
    old_base_raw = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    new_base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    new_hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    arr_new = np.array(new_base_raw)
    mask_new_bg = (arr_new[:, :, 0] > 240) & (arr_new[:, :, 1] > 240) & (arr_new[:, :, 2] > 240)
    arr_new[mask_new_bg, 3] = 0
    
    arr_old = np.array(old_base_raw)
    
    # Hair is only in the top half (Y < 650)
    diff = np.abs(arr_old[:, :, :3].astype(float) - arr_new[:, :, :3].astype(float))
    diff_mask = np.any(diff > 15, axis=2)
    
    gt_hair_mask = diff_mask & (arr_old[:, :, 3] > 0)
    gt_hair_mask[650:, :] = False
    gt_hair_mask[300:500, 500:750] = False
    
    new_hair_arr = simple_key(new_hair_raw)
    new_hair_img = Image.fromarray(new_hair_arr)
    w, h = new_hair_img.size
    
    best_score = -1
    best_params = None
    
    # Grid search for scale, ox, oy
    scales = np.linspace(1.15, 1.45, 31)
    for s in scales:
        new_w = int(round(w * s))
        new_h = int(round(h * s))
        scaled = new_hair_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
        scaled_mask = np.array(scaled)[:, :, 3] > 0
        
        left_base = (1254 - new_w) / 2.0
        top_base = (1254 - new_h) / 2.0
        
        for ox in range(-25, 5, 1):
            for oy in range(60, 140, 1):
                left = int(round(left_base + ox))
                top = int(round(top_base - oy))
                
                # Canvas matching
                canvas = np.zeros((1254, 1254), dtype=bool)
                
                c_min_y = top
                c_min_x = left
                c_max_y = c_min_y + new_h
                c_max_x = c_min_x + new_w
                
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
                score = intersection / (union + 1e-5)
                
                if score > best_score:
                    best_score = score
                    best_params = (s, ox, oy)
                    
    s, ox, oy = best_params
    print(f"Optimal alignment: scale={s:.4f}, ox={ox}, oy={oy} with IoU={best_score:.4f}")
    
    # Save the optimal composite to verify it visually
    new_w = int(round(w * s))
    new_h = int(round(h * s))
    scaled = new_hair_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    left = int(round((1254 - new_w) / 2.0 + ox))
    top = int(round((1254 - new_h) / 2.0 - oy))
    
    # Composite hair on new_base body
    comp = Image.fromarray(arr_new).copy()
    comp.paste(scaled, (left, top), scaled)
    comp.save("scratch/hair_optimal_composite.png")
    print("Saved optimal composite to scratch/hair_optimal_composite.png")

if __name__ == "__main__":
    main()

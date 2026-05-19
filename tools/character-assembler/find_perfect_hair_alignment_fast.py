import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask] = 0
    return Image.fromarray(arr)

def main():
    base = simple_key(Image.open("tmp/base-no-hair-eyes.png").convert("RGBA"))
    hair = simple_key(Image.open("tmp/hair.png").convert("RGBA"))
    orig = simple_key(Image.open("tmp/base.png").convert("RGBA"))
    o_arr = np.array(orig)
    
    best_err = float('inf')
    best_s = 0.0
    best_left = 0
    best_top = 0
    
    base_arr = np.array(base)
    # We will search scale from 0.53 to 0.57 with 9 steps
    for s in np.linspace(0.53, 0.57, 9):
        new_w = int(round(hair.width * s))
        new_h = int(round(hair.height * s))
        scaled_hair = hair.resize((new_w, new_h), Image.Resampling.BILINEAR)
        s_arr = np.array(scaled_hair)
        
        # Estimate base left/top
        ys, xs = np.where(s_arr[:, :, 3] > 0)
        s_act_top = ys.min()
        s_act_cx = xs.min() + (xs.max() - xs.min()) / 2.0
        
        est_left = int(round(627.0 - s_act_cx))
        est_top = int(round(29.0 - s_act_top))
        
        for dx in range(-12, 13):
            for dy in range(-12, 13):
                left = est_left + dx
                top = est_top + dy
                
                # Check bounds
                if left < 0 or top < 0 or left + new_w > 1254 or top + new_h > 1254:
                    continue
                    
                # Alpha composite s_arr on top of base_arr
                # We can do this very fast in NumPy:
                # Copy base_arr
                c_arr = base_arr.copy()
                
                # Alpha blend s_arr onto c_arr at top:top+new_h, left:left+new_w
                target = c_arr[top:top+new_h, left:left+new_w].astype(float)
                src = s_arr.astype(float)
                
                alpha_src = src[:, :, 3:4] / 255.0
                alpha_tgt = target[:, :, 3:4] / 255.0
                
                out_alpha = alpha_src + alpha_tgt * (1.0 - alpha_src)
                # Avoid division by zero
                out_alpha_safe = np.where(out_alpha > 0, out_alpha, 1.0)
                
                out_rgb = (src[:, :, :3] * alpha_src + target[:, :, :3] * alpha_tgt * (1.0 - alpha_src)) / out_alpha_safe
                
                blend = np.zeros_like(target)
                blend[:, :, :3] = np.clip(out_rgb, 0, 255)
                blend[:, :, 3] = np.clip(out_alpha * 255.0, 0, 255)
                
                c_arr[top:top+new_h, left:left+new_w] = blend.astype(np.uint8)
                
                # Compute difference over the bounding box of the head [0:600, 300:950]
                diff = np.mean(np.abs(c_arr[0:600, 300:950].astype(float) - o_arr[0:600, 300:950].astype(float)))
                if diff < best_err:
                    best_err = diff
                    best_s = s
                    best_left = left
                    best_top = top
                    
    print(f"Optimal scale s: {best_s:.4f}")
    print(f"Optimal left: {best_left}, top: {best_top}")
    print(f"Minimum Error: {best_err:.4f}")
    
    # Let's save the optimal composite
    scaled_hair = hair.resize((int(round(hair.width * best_s)), int(round(hair.height * best_s))), Image.Resampling.BILINEAR)
    comp = base.copy()
    comp.paste(scaled_hair, (best_left, best_top), scaled_hair)
    comp.save("scratch/perfect_hair_fit_final.png")
    
    # Compute Bevy/TOML parameters
    new_w = int(round(hair.width * best_s))
    new_h = int(round(hair.height * best_s))
    placed_cx = best_left + new_w / 2.0
    placed_cy = best_top + new_h / 2.0
    toml_x = placed_cx - 627.0
    toml_y = 627.0 - placed_cy
    print(f"Calculated TOML: scale = {best_s:.4f}, offset = {{ x = {toml_x:.2f}, y = {toml_y:.2f} }}")

if __name__ == "__main__":
    main()

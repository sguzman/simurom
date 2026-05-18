import numpy as np
import math
from PIL import Image

def bilinear_sample(img_arr, x, y):
    h, w = img_arr.shape[:2]
    if x < 0 or x >= w - 1 or y < 0 or y >= h - 1:
        if x >= -0.5 and x < w - 0.5 and y >= -0.5 and y < h - 0.5:
            px = int(round(max(0.0, min(w - 1.0, x))))
            py = int(round(max(0.0, min(h - 1.0, y))))
            return img_arr[py, px]
        return None
    
    x0 = int(math.floor(x))
    x1 = x0 + 1
    y0 = int(math.floor(y))
    y1 = y0 + 1
    
    dx = x - x0
    dy = y - y0
    
    p00 = img_arr[y0, x0].astype(float)
    p10 = img_arr[y0, x1].astype(float)
    p01 = img_arr[y1, x0].astype(float)
    p11 = img_arr[y1, x1].astype(float)
    
    val = p00 * (1.0 - dx) * (1.0 - dy) + p10 * dx * (1.0 - dy) + p01 * (1.0 - dx) * dy + p11 * dx * dy
    return np.clip(np.round(val), 0, 255).astype(np.uint8)

def transform_layer(layer_path, base_size, s, r, offset_x, offset_y):
    layer_img = Image.open(layer_path).convert("RGBA")
    layer_arr = np.array(layer_img)
    
    comp_arr = np.zeros((base_size[1], base_size[0], 4), dtype=np.uint8)
    
    target_cx = base_size[0] / 2.0
    target_cy = base_size[1] / 2.0
    src_cx = layer_arr.shape[1] / 2.0
    src_cy = layer_arr.shape[0] / 2.0
    
    angle_rad = -math.radians(r)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    for ty in range(base_size[1]):
        for tx in range(base_size[0]):
            x3 = (tx - target_cx) - offset_x
            y3 = (target_cy - ty) - offset_y
            
            x2 = x3 * cos_a - y3 * sin_a
            y2 = x3 * sin_a + y3 * cos_a
            
            x1 = x2 / s
            y1 = y2 / s
            
            sx = x1 + src_cx
            sy = src_cy - y1
            
            sample = bilinear_sample(layer_arr, sx, sy)
            if sample is not None and sample[3] > 0:
                comp_arr[ty, tx] = sample
                
    return Image.fromarray(comp_arr)

def main():
    base_size = (1254, 1254)
    base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    eyes = transform_layer("assets/mini_game/images/blonde_eyes_open.png", base_size, 0.2225, 10.25, -19.6, 363.0)
    
    # We will test eyebrows offsets y from 390 to 420
    for oy in [390.0, 400.0, 410.0, 420.0]:
        brows = transform_layer("assets/mini_game/images/blonde_eyebrows.png", base_size, 0.24, 10.25, -25.0, oy)
        
        composite = base.copy()
        composite.paste(eyes, (0, 0), eyes)
        composite.paste(brows, (0, 0), brows)
        
        # Crop head region
        crop = composite.crop((450, 100, 800, 450))
        crop.save(f"scratch/composite_brows_oy_{int(oy)}.png")
        print(f"Saved offset_y = {oy} preview to scratch/composite_brows_oy_{int(oy)}.png")

if __name__ == "__main__":
    main()

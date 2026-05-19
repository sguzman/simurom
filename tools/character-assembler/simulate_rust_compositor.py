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
    
    val0 = p00 * (1.0 - dx) + p10 * dx
    val1 = p01 * (1.0 - dx) + p11 * dx
    val = val0 * (1.0 - dy) + val1 * dy
    
    return np.clip(np.round(val), 0, 255).astype(np.uint8)

def main():
    # Let's load the eyebrows image
    eyebrows = Image.open("assets/mini_game/images/blonde_eyebrows.png").convert("RGBA")
    eb_arr = np.array(eyebrows)
    
    base_size = (1254, 1254)
    composite = Image.new("RGBA", base_size, (0, 0, 0, 0))
    comp_arr = np.array(composite)
    
    # Transform parameters for eyebrows
    s = 0.24
    r = 10.25
    offset_x = -25.0
    offset_y = 380.0
    
    target_cx = base_size[0] / 2.0
    target_cy = base_size[1] / 2.0
    src_cx = eb_arr.shape[1] / 2.0
    src_cy = eb_arr.shape[0] / 2.0
    
    angle_rad = -math.radians(r)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Let's perform the same loop as Rust
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
            
            sample = bilinear_sample(eb_arr, sx, sy)
            if sample is not None:
                if sample[3] > 0:
                    comp_arr[ty, tx] = sample
                    
    # Save the composite of eyebrows alone
    Image.fromarray(comp_arr).save("scratch/eyebrows_simulated_alone.png")
    
    # Check if there are any non-transparent pixels
    non_transparent = comp_arr[:,:,3] > 0
    print("Non-transparent pixels in simulated composite:", np.sum(non_transparent))
    
    y_indices, x_indices = np.where(non_transparent)
    if len(y_indices) > 0:
        print("Y range of simulated eyebrows:", y_indices.min(), "to", y_indices.max())
        print("X range of simulated eyebrows:", x_indices.min(), "to", x_indices.max())
    else:
        print("No pixels ended up on the canvas!")

if __name__ == "__main__":
    main()

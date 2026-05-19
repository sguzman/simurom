import numpy as np
from PIL import Image

def get_rotated_scaled_eyes_bbox():
    # Let's open the eyes image
    eyes_img = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Let's apply the exact scale and rotation from blonde.toml
    # scale = 0.2225, rotation = 10.25, offset = { x = -19.6, y = 363.0 }
    scale = 0.2225
    rotation = 10.25
    offset_x = -19.6
    offset_y = 363.0
    
    w, h = eyes_img.size
    
    # We will composite onto a 1254x1254 transparent canvas
    base_size = (1254, 1254)
    canvas = Image.new("RGBA", base_size, (0, 0, 0, 0))
    
    # Replicate the exact transformation in python (matching simurom-character-cli)
    # The transform in simurom-character-cli is:
    # let target_cx = base_size.0 as f32 / 2.0; (627)
    # let target_cy = base_size.1 as f32 / 2.0; (627)
    # let src_cx = layer_img.width() as f32 / 2.0; (w/2)
    # let src_cy = layer_img.height() as f32 / 2.0; (h/2)
    # let angle_rad = -r.to_radians();
    # x3 = tx - target_cx - offset_x
    # y3 = target_cy - ty - offset_y
    # x2 = x3 * cos - y3 * sin
    # y2 = x3 * sin + y3 * cos
    # x1 = x2 / s
    # y1 = y2 / s
    # sx = x1 + src_cx
    # sy = src_cy - y1
    
    target_cx = 1254 / 2.0
    target_cy = 1254 / 2.0
    src_cx = w / 2.0
    src_cy = h / 2.0
    
    import math
    angle_rad = -math.radians(rotation)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # We can do this efficiently using PIL affine transform
    # The forward mapping from source coordinate (sx, sy) relative to center to target coordinate (tx, ty) relative to center is:
    # tx_rel = sx_rel * s * cos_a - sy_rel * s * -sin_a + offset_x
    # ty_rel = sx_rel * s * sin_a + sy_rel * s * cos_a + offset_y
    # Since y direction is inverted in image coordinates compared to cartesian:
    # let's just do pixel-by-pixel rendering or use PIL's transform
    
    # Let's do pixel by pixel for 100% exact correctness matching Bevy / Rust CLI
    canvas_arr = np.zeros((1254, 1254, 4), dtype=np.uint8)
    eyes_arr = np.array(eyes_img)
    
    for ty in range(1254):
        for tx in range(1254):
            x3 = (tx - target_cx) - offset_x
            y3 = (target_cy - ty) - offset_y
            
            x2 = x3 * cos_a - y3 * sin_a
            y2 = x3 * sin_a + y3 * cos_a
            
            x1 = x2 / scale
            y1 = y2 / scale
            
            sx = x1 + src_cx
            sy = src_cy - y1
            
            # Bilinear or nearest neighbor
            if sx >= 0 and sx < w - 1 and sy >= 0 and sy < h - 1:
                # Nearest neighbor for simple bbox find
                psx = int(round(sx))
                psy = int(round(sy))
                canvas_arr[ty, tx] = eyes_arr[psy, psx]
                
    # Find bounding box of non-transparent pixels
    alpha = canvas_arr[:, :, 3]
    y_indices, x_indices = np.where(alpha > 0)
    if len(x_indices) > 0:
        min_x, max_x = np.min(x_indices), np.max(x_indices)
        min_y, max_y = np.min(y_indices), np.max(y_indices)
        print(f"BBox: X [{min_x}, {max_x}], Y [{min_y}, {max_y}]")
        print(f"Width: {max_x - min_x + 1}, Height: {max_y - min_y + 1}")
        
        # Save cropped image to inspect
        cropped = Image.fromarray(canvas_arr[min_y:max_y+1, min_x:max_x+1])
        cropped.save("scratch/eyes_only_cropped.png")
    else:
        print("No non-transparent pixels found!")

if __name__ == "__main__":
    get_rotated_scaled_eyes_bbox()

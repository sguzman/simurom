import numpy as np
from PIL import Image
from collections import deque

def key_out_white(img):
    arr = np.array(img.convert("RGBA"))
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    # Corners
    corners = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
    for cx, cy in corners:
        if arr[cy, cx, 0] > 240 and arr[cy, cx, 1] > 240 and arr[cy, cx, 2] > 240:
            if not visited[cy, cx]:
                visited[cy, cx] = True
                queue.append((cx, cy))
                
    while queue:
        cx, cy = queue.popleft()
        arr[cy, cx, 3] = 0
        
        for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
            if 0 <= nx < w and 0 <= ny < h:
                if not visited[ny, nx]:
                    if arr[ny, nx, 0] > 240 and arr[ny, nx, 1] > 240 and arr[ny, nx, 2] > 240:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
    return Image.fromarray(arr)

def main():
    base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    eyes_raw = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    brows_raw = Image.open("tmp/eye-brows.png").convert("RGBA")
    
    brows = key_out_white(brows_raw)
    
    # 1. Paste eyes: scale = 0.2225, rotation = 10.25, cx = 607.4, cy = 264.0 (derived from offset = -19.6, 363.0)
    # Let's use the exact composite math:
    # cx = bevy_x + 627.0 = -19.6 + 627.0 = 607.4
    # cy = 627.0 - bevy_y = 627.0 - 363.0 = 264.0
    eye_scale = 0.2225
    eye_angle = 10.25
    eye_cx = 607.4
    eye_cy = 264.0
    
    eyes_crop = eyes_raw.crop((278, 482, 973, 717))
    w_new = int((973 - 278) * eye_scale)
    h_new = int((717 - 482) * eye_scale)
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    eyes_rotated = eyes_resized.rotate(eye_angle, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = eyes_rotated.size
    
    x_left = int(eye_cx - w_rot / 2)
    y_top = int(eye_cy - h_rot / 2)
    
    composite = base.copy()
    composite.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
    
    # 2. Paste brows: scale = 0.2400, rotation = 10.25, cx = 602.0, cy = 247.0 (derived from offset = -25.0, 380.0)
    brow_scale = 0.2400
    brow_angle = 10.25
    brow_cx = 602.0
    brow_cy = 247.0
    
    brows_crop = brows.crop((301, 580, 952, 655))
    w_new = int((952 - 301) * brow_scale)
    h_new = int((655 - 580) * brow_scale)
    brows_resized = brows_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    brows_rotated = brows_resized.rotate(brow_angle, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = brows_rotated.size
    
    x_left = int(brow_cx - w_rot / 2)
    y_top = int(brow_cy - h_rot / 2)
    
    composite.paste(brows_rotated, (x_left, y_top), brows_rotated)
    composite.save("scratch/composite_with_brows.png")
    
    # Also save head crop
    head = composite.crop((450, 100, 800, 450))
    head.save("scratch/head_with_brows.png")
    print("Saved composite and crop to scratch/composite_with_brows.png and head_with_brows.png")

if __name__ == "__main__":
    main()

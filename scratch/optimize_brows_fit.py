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
    # Load original reference image (which has eyebrows on face)
    img_ref = Image.open("tmp/base.png").convert("RGB")
    arr_ref = np.array(img_ref)
    
    # Load base image (without eyebrows or eyes)
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    
    # Load eyebrows image and key out white
    img_brows_raw = Image.open("tmp/eye-brows.png").convert("RGBA")
    img_brows = key_out_white(img_brows_raw)
    
    # Bounding box of eyebrows in raw image is X: 301 to 952, Y: 580 to 655
    brows_crop = img_brows.crop((301, 580, 952, 655))
    src_w = 952 - 301
    src_h = 655 - 580
    
    # Evaluation region for eyebrows on the face: Y in [210, 260], X in [530, 690]
    eval_y0, eval_y1 = 210, 260
    eval_x0, eval_x1 = 530, 690
    ref_crop = arr_ref[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
    
    def evaluate(scale, angle, cx, cy):
        w_new = int(src_w * scale)
        h_new = int(src_h * scale)
        if w_new <= 0 or h_new <= 0:
            return 1e9
            
        brows_resized = brows_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
        brows_rotated = brows_resized.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        w_rot, h_rot = brows_rotated.size
        
        x_left = int(cx - w_rot / 2)
        y_top = int(cy - h_rot / 2)
        
        # Paste onto transparent base
        comp_rgba = img_b.copy()
        comp_rgba.paste(brows_rotated, (x_left, y_top), brows_rotated)
        
        # Flatten onto white background
        comp_rgb = Image.new("RGB", comp_rgba.size, (255, 255, 255))
        comp_rgb.paste(comp_rgba, mask=comp_rgba.split()[3])
        
        # Evaluate loss in eyebrow region
        arr_comp = np.array(comp_rgb)[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
        diff = np.abs(ref_crop - arr_comp)
        
        return diff.sum()

    print("Starting coarse search...")
    # Coarse search ranges
    # Since eyebrows are drawn by the same artist, their scale/angle might be identical or close to eyes
    scales = [0.18, 0.20, 0.22, 0.24, 0.26]
    angles = [6.0, 8.0, 10.25, 12.0, 14.0]
    # Let's search cx, cy. On the 1254x1254 canvas:
    # Eyes center is X=608, Y=255. Eyebrows should be slightly higher (smaller Y in image space)
    cxs = [600.0, 608.0, 616.0]
    cys = [225.0, 235.0, 245.0]
    
    best_loss = 1e12
    best_params = None
    
    for s in scales:
        for a in angles:
            for cx in cxs:
                for cy in cys:
                    loss = evaluate(s, a, cx, cy)
                    if loss < best_loss:
                        best_loss = loss
                        best_params = (s, a, cx, cy)
                        
    print(f"Coarse search best: scale={best_params[0]}, angle={best_params[1]}, cx={best_params[2]}, cy={best_params[3]} | loss={best_loss}")
    
    # Fine search
    print("Starting fine search...")
    s_best, a_best, cx_best, cy_best = best_params
    
    fine_scales = [s_best + d for d in [-0.015, -0.007, 0, 0.007, 0.015]]
    fine_angles = [a_best + d for d in [-1.5, -0.75, 0, 0.75, 1.5]]
    fine_cxs = [cx_best + d for d in [-2.0, -1.0, 0, 1.0, 2.0]]
    fine_cys = [cy_best + d for d in [-2.0, -1.0, 0, 1.0, 2.0]]
    
    for s in fine_scales:
        for a in fine_angles:
            for cx in fine_cxs:
                for cy in fine_cys:
                    loss = evaluate(s, a, cx, cy)
                    if loss < best_loss:
                        best_loss = loss
                        best_params = (s, a, cx, cy)
                        
    opt_scale, opt_angle, opt_cx, opt_cy = best_params
    print(f"Fine search best: scale={opt_scale:.4f}, angle={opt_angle:.2f}, cx={opt_cx:.2f}, cy={opt_cy:.2f} | loss={best_loss}")
    
    # Print Bevy TOML equivalent parameters:
    # Scale: opt_scale
    # Rotation: opt_angle
    # Offset center translation:
    # Bevy Y is inverted. Let's calculate:
    # Target center on canvas:
    # target_x = opt_cx - (1254 / 2) = opt_cx - 627
    # target_y = (1254 / 2) - opt_cy = 627 - opt_cy
    bevy_x = opt_cx - 627.0
    bevy_y = 627.0 - opt_cy
    print(f"Bevy TOML equivalent: scale={opt_scale:.4f}, rotation={opt_angle:.2f}, offset = {{ x = {bevy_x:.2f}, y = {bevy_y:.2f} }}")

if __name__ == "__main__":
    main()

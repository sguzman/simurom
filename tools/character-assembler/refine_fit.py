import numpy as np
from PIL import Image

def main():
    img_ref = Image.open("tmp/base.png").convert("RGB")
    arr_ref = np.array(img_ref)
    
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    eyes_crop = img_e.crop((278, 482, 973, 717))
    
    eval_y0, eval_y1 = 200, 310
    eval_x0, eval_x1 = 530, 690
    ref_crop = arr_ref[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
    
    def evaluate(scale, angle, cx, cy):
        w_new = int(695 * scale)
        h_new = int(235 * scale)
        if w_new <= 0 or h_new <= 0:
            return 1e9
            
        eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
        eyes_rotated = eyes_resized.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        w_rot, h_rot = eyes_rotated.size
        
        x_left = int(cx - w_rot / 2)
        y_top = int(cy - h_rot / 2)
        
        comp_rgba = img_b.copy()
        comp_rgba.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
        
        comp_rgb = Image.new("RGB", comp_rgba.size, (255, 255, 255))
        comp_rgb.paste(comp_rgba, mask=comp_rgba.split()[3])
        
        arr_comp = np.array(comp_rgb)[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
        diff = np.abs(ref_crop - arr_comp)
        return diff.sum()

    # Best parameters from previous run: scale=0.22, angle=10.5, cx=606.0, cy=259.0
    # Let's search with smaller steps
    scales = np.linspace(0.205, 0.235, 13) # step 0.0025
    angles = np.linspace(9.5, 11.5, 9)     # step 0.25
    cxs = np.linspace(603.0, 609.0, 13)    # step 0.5
    cys = np.linspace(256.0, 262.0, 13)    # step 0.5
    
    best_loss = 1e12
    best_params = (0.22, 10.5, 606.0, 259.0)
    
    # We will do coordinate descent to keep it extremely fast
    # Coordinate descent iterates over each parameter, keeping the others fixed, and repeats
    curr_s, curr_a, curr_cx, curr_cy = best_params
    
    for iteration in range(3):
        # Optimize scale
        best_s = curr_s
        for s in np.linspace(curr_s - 0.015, curr_s + 0.015, 13):
            loss = evaluate(s, curr_a, curr_cx, curr_cy)
            if loss < best_loss:
                best_loss = loss
                best_s = s
        curr_s = best_s
        
        # Optimize angle
        best_a = curr_a
        for a in np.linspace(curr_a - 1.5, curr_a + 1.5, 13):
            loss = evaluate(curr_s, a, curr_cx, curr_cy)
            if loss < best_loss:
                best_loss = loss
                best_a = a
        curr_a = best_a
        
        # Optimize cx
        best_cx = curr_cx
        for cx in np.linspace(curr_cx - 3.0, curr_cx + 3.0, 13):
            loss = evaluate(curr_s, curr_a, cx, curr_cy)
            if loss < best_loss:
                best_loss = loss
                best_cx = cx
        curr_cx = best_cx
        
        # Optimize cy
        best_cy = curr_cy
        for cy in np.linspace(curr_cy - 3.0, curr_cy + 3.0, 13):
            loss = evaluate(curr_s, curr_a, curr_cx, cy)
            if loss < best_loss:
                best_loss = loss
                best_cy = cy
        curr_cy = best_cy
        
        print(f"Iteration {iteration+1} best: scale={curr_s:.4f}, angle={curr_a:.2f}, cx={curr_cx:.2f}, cy={curr_cy:.2f} | loss={best_loss}")
        
    # Render final optimized image
    w_new = int(695 * curr_s)
    h_new = int(235 * curr_s)
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    eyes_rotated = eyes_resized.rotate(curr_a, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = eyes_rotated.size
    x_left = int(curr_cx - w_rot / 2)
    y_top = int(curr_cy - h_rot / 2)
    
    opt_comp = img_b.copy()
    opt_comp.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
    opt_comp.save("scratch/opt_placement.png")
    opt_comp.crop((450, 50, 750, 380)).save("scratch/opt_head.png")
    
    print(f"Final parameters: scale={curr_s:.5f}, angle={curr_a:.3f}, cx={curr_cx:.3f}, cy={curr_cy:.3f}")

if __name__ == "__main__":
    main()

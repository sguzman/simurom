import numpy as np
from PIL import Image

def main():
    # Load original reference image with eyes
    img_ref = Image.open("tmp/base.png").convert("RGB")
    arr_ref = np.array(img_ref)
    
    # Load base image (without eyes) and eye image
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    img_e = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Crop the eyes out of blonde_eyes_open.png
    eyes_crop = img_e.crop((278, 482, 973, 717))
    
    # Evaluation region: Y in [200, 310], X in [530, 690]
    eval_y0, eval_y1 = 200, 310
    eval_x0, eval_x1 = 530, 690
    ref_crop = arr_ref[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
    
    # Pre-render a white background canvas for pasting
    bg_w, bg_h = img_b.size
    
    def evaluate(scale, angle, cx, cy):
        # Resize eyes
        w_new = int(695 * scale)
        h_new = int(235 * scale)
        if w_new <= 0 or h_new <= 0:
            return 1e9
            
        eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
        
        # Rotate eyes
        eyes_rotated = eyes_resized.rotate(angle, Image.Resampling.BICUBIC, expand=True)
        w_rot, h_rot = eyes_rotated.size
        
        x_left = int(cx - w_rot / 2)
        y_top = int(cy - h_rot / 2)
        
        # Paste onto transparent base
        comp_rgba = img_b.copy()
        comp_rgba.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
        
        # Flatten onto white background
        comp_rgb = Image.new("RGB", comp_rgba.size, (255, 255, 255))
        comp_rgb.paste(comp_rgba, mask=comp_rgba.split()[3])
        
        # Evaluate loss in face region
        arr_comp = np.array(comp_rgb)[eval_y0:eval_y1, eval_x0:eval_x1].astype(float)
        diff = np.abs(ref_crop - arr_comp)
        
        return diff.sum()

    print("Starting coarse search...")
    # Coarse search ranges
    scales = [0.17, 0.18, 0.19, 0.20, 0.21]
    angles = [8.0, 10.5, 13.0]
    cxs = [608.0, 612.0, 616.0]
    cys = [251.0, 255.0, 259.0]
    
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
    
    # Fine search around coarse best
    print("Starting fine search...")
    s_best, a_best, cx_best, cy_best = best_params
    
    fine_scales = [s_best + d for d in [-0.01, -0.005, 0, 0.005, 0.01]]
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
    
    # Render and save best
    w_new = int(695 * opt_scale)
    h_new = int(235 * opt_scale)
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    eyes_rotated = eyes_resized.rotate(opt_angle, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = eyes_rotated.size
    x_left = int(opt_cx - w_rot / 2)
    y_top = int(opt_cy - h_rot / 2)
    
    opt_comp = img_b.copy()
    opt_comp.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
    opt_comp.save("scratch/opt_placement.png")
    opt_comp.crop((450, 50, 750, 380)).save("scratch/opt_head.png")
    
    print("Successfully saved optimized images to scratch/opt_placement.png and scratch/opt_head.png")

if __name__ == "__main__":
    main()

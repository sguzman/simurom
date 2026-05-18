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
    
    s = 0.54
    new_w = int(round(hair.width * s))
    new_h = int(round(hair.height * s))
    scaled_hair = hair.resize((new_w, new_h), Image.Resampling.BILINEAR)
    s_arr = np.array(scaled_hair)
    
    ys, xs = np.where(s_arr[:, :, 3] > 0)
    s_act_top = ys.min()
    s_act_cx = xs.min() + (xs.max() - xs.min()) / 2.0
    
    left = int(round(627.0 - s_act_cx))
    top = int(round(29.0 - s_act_top))
    
    c_arr = np.array(base).copy()
    target = c_arr[top:top+new_h, left:left+new_w].astype(float)
    src = s_arr.astype(float)
    
    alpha_src = src[:, :, 3:4] / 255.0
    alpha_tgt = target[:, :, 3:4] / 255.0
    
    out_alpha = alpha_src + alpha_tgt * (1.0 - alpha_src)
    out_alpha_safe = np.where(out_alpha > 0, out_alpha, 1.0)
    
    out_rgb = (src[:, :, :3] * alpha_src + target[:, :, :3] * alpha_tgt * (1.0 - alpha_src)) / out_alpha_safe
    
    blend = np.zeros_like(target)
    blend[:, :, :3] = np.clip(out_rgb, 0, 255)
    blend[:, :, 3] = np.clip(out_alpha * 255.0, 0, 255)
    
    c_arr[top:top+new_h, left:left+new_w] = blend.astype(np.uint8)
    
    diff = np.mean(np.abs(c_arr[0:600, 300:950].astype(float) - o_arr[0:600, 300:950].astype(float)))
    print(f"diff value: {diff}, is nan: {np.isnan(diff)}")

if __name__ == "__main__":
    main()

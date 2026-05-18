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
    
    # We want to find the exact uniform scale `s` and position (x, y)
    # for `hair` to fit perfectly onto `base` to match `orig`.
    # Let's try some manual/visual scales:
    # Scale ~ 0.53, 0.54, 0.55, 0.56, 0.57
    
    # Since orig has hair top at y=29, and hair center at x=627 (since the canvas is 1254x1254 and it's centered),
    # let's look at the bounds of the hair in tmp/hair.png:
    # Hair in tmp/hair.png has active y-range 99 to 1030, active x-range 279 to 1069.
    # The active height is 931. The active width is 790.
    # The head of the character in base-no-hair-eyes.png is centered at x=627, top at y=106.
    
    for s in [0.52, 0.54, 0.55, 0.56, 0.57, 0.58, 0.60]:
        new_w = int(round(hair.width * s))
        new_h = int(round(hair.height * s))
        scaled_hair = hair.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        # We want to place it. Let's find the y-offset.
        # If the top of the scaled hair's active pixels should line up near y=29 (the top of the hair in the baked version):
        # Let's find the active top of the scaled hair:
        s_arr = np.array(scaled_hair)
        ys, xs = np.where(s_arr[:, :, 3] > 0)
        s_act_top = ys.min()
        s_act_cx = xs.min() + (xs.max() - xs.min()) / 2.0
        
        # We want the placed hair's active top to be at y=29.
        # So top = 29 - s_act_top
        # And the horizontal center of the active hair to be at x=627.
        # So left = 627 - s_act_cx
        
        left = int(round(627.0 - s_act_cx))
        top = int(round(29.0 - s_act_top))
        
        # Paste
        canvas = base.copy()
        canvas.paste(scaled_hair, (left, top), scaled_hair)
        
        # Save preview
        canvas.save(f"scratch/hair_scale_{s:.2f}.png")
        
        # Let's check difference against orig in the hair region (y from 29 to 600, x from 300 to 950)
        c_arr = np.array(canvas)
        o_arr = np.array(orig)
        diff = np.mean(np.abs(c_arr[29:600, 300:950].astype(float) - o_arr[29:600, 300:950].astype(float)))
        print(f"Scale: {s:.2f} | left={left}, top={top} | diff={diff:.4f}")
        
        # Bevy/TOML parameters:
        # placed center: cx = left + new_w / 2.0, cy = top + new_h / 2.0
        # TOML x offset = cx - 627.0
        # TOML y offset = 627.0 - cy
        cx = left + new_w / 2.0
        cy = top + new_h / 2.0
        tx = cx - 627.0
        ty = 627.0 - cy
        print(f"  TOML: scale = {s:.4f}, offset = {{ x = {tx:.2f}, y = {ty:.2f} }}")

if __name__ == "__main__":
    main()

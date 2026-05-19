import numpy as np
from PIL import Image

def get_bbox(img):
    arr = np.array(img)
    mask = arr[:, :, 3] > 0
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return (xs.min(), ys.min(), xs.max(), ys.max())

def main():
    base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    base_orig_raw = Image.open("tmp/base.png").convert("RGBA")
    hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    # Key out white backgrounds
    def get_clean_alpha(img):
        arr = np.array(img)
        mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
        arr[mask, 3] = 0
        return arr[:, :, 3]
        
    base_a = get_clean_alpha(base_raw)
    base_orig_a = get_clean_alpha(base_orig_raw)
    hair_a = get_clean_alpha(hair_raw)
    
    # Hair in original image is:
    orig_hair_mask = (base_orig_a > 0) & (base_a == 0)
    ys, xs = np.where(orig_hair_mask)
    print(f"Orig hair y-range: {ys.min()} to {ys.max()} (height = {ys.max() - ys.min() + 1})")
    print(f"Orig hair x-range: {xs.min()} to {xs.max()} (width = {xs.max() - xs.min() + 1})")
    
    # Hair in tmp/hair.png is:
    ys2, xs2 = np.where(hair_a > 0)
    print(f"tmp/hair.png y-range: {ys2.min()} to {ys2.max()} (height = {ys2.max() - ys2.min() + 1})")
    print(f"tmp/hair.png x-range: {xs2.min()} to {xs2.max()} (width = {xs2.max() - xs2.min() + 1})")

if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def main():
    old_base_raw = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    new_base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    
    arr_new = np.array(new_base_raw)
    mask_new_bg = (arr_new[:, :, 0] > 240) & (arr_new[:, :, 1] > 240) & (arr_new[:, :, 2] > 240)
    arr_new[mask_new_bg, 3] = 0
    
    arr_old = np.array(old_base_raw)
    
    diff = np.abs(arr_old[:, :, :3].astype(float) - arr_new[:, :, :3].astype(float))
    diff_mask = np.any(diff > 15, axis=2)
    
    # Hair is only in the top half (Y < 650)
    hair_diff_mask = diff_mask & (arr_old[:, :, 3] > 0)
    hair_diff_mask[650:, :] = False
    
    # Exclude eyes region
    hair_diff_mask[300:500, 500:750] = False
    
    # Save the mask to inspect it
    mask_img = Image.fromarray((hair_diff_mask * 255).astype(np.uint8))
    mask_img.save("scratch/hair_difference_mask.png")
    print(f"Refined mask has {np.sum(hair_diff_mask)} active pixels.")

if __name__ == "__main__":
    main()

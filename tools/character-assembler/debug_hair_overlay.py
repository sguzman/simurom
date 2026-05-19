import numpy as np
from PIL import Image

def main():
    old_base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    new_hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    # Key out white background of new_hair
    arr = np.array(new_hair_raw)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    new_hair = Image.fromarray(arr)
    
    # Let's save a composite where we draw the new hair in semi-transparent red on top of the old base!
    # This will show us EXACTLY how they are shifted relative to each other!
    overlay = old_base.copy()
    red_hair = Image.new("RGBA", new_hair.size)
    red_arr = np.array(new_hair)
    # Make all non-transparent pixels red
    non_trans = red_arr[:, :, 3] > 0
    red_arr[non_trans] = [255, 0, 0, 150] # semi-transparent red
    red_hair_img = Image.fromarray(red_arr)
    
    overlay.paste(red_hair_img, (0, 0), red_hair_img)
    overlay.crop((350, 50, 900, 600)).save("scratch/hair_alignment_debug.png")
    print("Saved hair alignment debug image to scratch/hair_alignment_debug.png")

if __name__ == "__main__":
    main()

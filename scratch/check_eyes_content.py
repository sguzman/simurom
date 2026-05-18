import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    # Let's crop the eye/eyebrow region in the raw eyes asset: X: 550 to 700, Y: 200 to 300
    crop = img.crop((550, 200, 700, 300))
    crop.save("scratch/inspect_eyes_raw_forehead.png")
    
    # Check if there are non-transparent pixels in this region
    arr = np.array(crop)
    non_transparent = arr[:,:,3] > 0
    print("Non-transparent pixels in raw eyes forehead region (550-700, 200-300):", np.sum(non_transparent))
    
    # Let's do the same for the actual composite layers to see if the eyes layer overwrites this region!
    # Let's simulate composite of just body + eyebrows, and then body + eyebrows + eyes
    # and compare the two forehead crops!
    
    base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    eyebrows = Image.open("scratch/eyebrows_simulated_alone.png").convert("RGBA")
    
    # Composite body + eyebrows
    body_brows = base.copy()
    body_brows.paste(eyebrows, (0, 0), eyebrows)
    body_brows.save("scratch/composite_body_brows.png")
    
    # Save a crop of forehead
    crop_bb = body_brows.crop((450, 100, 800, 450))
    crop_bb.save("scratch/head_body_brows.png")
    
    print("Saved body+brows preview to scratch/head_body_brows.png")

if __name__ == "__main__":
    main()

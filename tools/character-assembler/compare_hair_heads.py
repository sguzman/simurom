import numpy as np
from PIL import Image

def main():
    old_base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    
    new_base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    new_hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    # Simple color key for flat white/light gray background (R,G,B > 240)
    def simple_key(img):
        arr = np.array(img)
        mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
        arr[mask, 3] = 0
        return Image.fromarray(arr)
        
    new_base = simple_key(new_base_raw)
    new_hair = simple_key(new_hair_raw)
    
    # Overlay new hair on new base directly at (0, 0)
    new_composite = new_base.copy()
    new_composite.paste(new_hair, (0, 0), new_hair)
    
    # Save cropped head comparisons
    old_head = old_base.crop((450, 100, 800, 450))
    old_head.save("scratch/head_old_base.png")
    
    new_head = new_composite.crop((450, 100, 800, 450))
    new_head.save("scratch/head_new_composite.png")
    
    print("Saved old vs new head composites to scratch/")

if __name__ == "__main__":
    main()

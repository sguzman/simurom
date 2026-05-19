import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    return Image.fromarray(arr)

def main():
    base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    base = simple_key(base_raw)
    hair = simple_key(hair_raw)
    
    # Let's composite them with scale = 1.0, offset = (0, 0)
    comp = base.copy()
    comp.paste(hair, (0, 0), hair)
    comp.save("scratch/test_hair_unscaled.png")
    
    # Also load base.png for comparison
    base_orig = simple_key(Image.open("tmp/base.png").convert("RGBA"))
    base_orig.save("scratch/test_base_orig.png")
    
    print("Generated test_hair_unscaled.png and test_base_orig.png!")

if __name__ == "__main__":
    main()

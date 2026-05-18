import numpy as np
from PIL import Image

def main():
    hair = Image.open("tmp/hair.png").convert("RGBA")
    arr = np.array(hair)
    
    # Let's save a visualization showing which pixels have R,G,B > 240 in red
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    vis = arr.copy()
    vis[mask] = [255, 0, 0, 255]
    
    Image.fromarray(vis).save("scratch/hair_high_threshold_mask.png")
    print("Saved high threshold mask visualization to scratch/hair_high_threshold_mask.png")

if __name__ == "__main__":
    main()

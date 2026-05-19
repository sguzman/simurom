import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr = np.array(img)
    
    # We restrict to Y in [0, 400], X in [400, 850]
    region = arr[0:400, 400:850]
    h, w = region.shape[:2]
    
    # Let's count and list pixels of different categories:
    # 1. Transparent (A == 0)
    # 2. Skin tone (R > 200, 130 < G < 210, 100 < B < 185)
    # 3. Yellow/Blonde Hair (R > 200, G > 180, B < 120) - wait, this overlaps skin sometimes. Let's see: hair is typically more saturated yellow (higher G and much lower B).
    # 4. Other colors (non-transparent, non-skin, non-hair)
    
    skin_mask = (region[:,:,0] > 200) & (region[:,:,1] > 130) & (region[:,:,1] < 210) & (region[:,:,2] > 100) & (region[:,:,2] < 185) & (region[:,:,3] > 0)
    transparent_mask = region[:,:,3] == 0
    
    hair_mask = (region[:,:,0] > 200) & (region[:,:,1] > 170) & (region[:,:,2] < 120) & (region[:,:,3] > 0) & (~skin_mask)
    
    other_mask = (region[:,:,3] > 0) & (~skin_mask) & (~hair_mask)
    
    print("Composition of head region:")
    print("Transparent pixels:", np.sum(transparent_mask))
    print("Skin pixels:", np.sum(skin_mask))
    print("Hair pixels:", np.sum(hair_mask))
    print("Other pixels:", np.sum(other_mask))
    
    # Let's print some coordinates of other pixels
    if np.sum(other_mask) > 0:
        other_y, other_x = np.where(other_mask)
        print("Other pixels bounding box:")
        print(f"Y: {other_y.min()} to {other_y.max()}")
        print(f"X: {other_x.min()} to {other_x.max()}")
        # Let's print some sample colors of "other" pixels
        unique_other = np.unique(region[other_mask].reshape(-1, 4), axis=0)
        print("Sample other colors (first 10):")
        for col in unique_other[:10]:
            print(col)

if __name__ == "__main__":
    main()

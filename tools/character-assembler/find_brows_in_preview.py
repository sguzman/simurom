import numpy as np
from PIL import Image

def main():
    preview = Image.open("artifacts/blonde_preview.png").convert("RGBA")
    arr = np.array(preview)
    h, w = arr.shape[:2]
    
    # Let's search for brown pixels that might belong to the eyebrows
    # Let's define the eyebrow color: R in [120, 180], G in [60, 110], B in [30, 80]
    mask = (arr[:,:,0] >= 120) & (arr[:,:,0] <= 180) & \
           (arr[:,:,1] >= 60) & (arr[:,:,1] <= 110) & \
           (arr[:,:,2] >= 30) & (arr[:,:,2] <= 80)
           
    print("Number of eyebrow-like pixels in the full preview:", np.sum(mask))
    
    # Let's see where they are concentrated
    y_indices, x_indices = np.where(mask)
    if len(y_indices) > 0:
        print("Y range:", y_indices.min(), "to", y_indices.max())
        print("X range:", x_indices.min(), "to", x_indices.max())
    else:
        print("No eyebrow-like pixels found in preview!")

if __name__ == "__main__":
    main()

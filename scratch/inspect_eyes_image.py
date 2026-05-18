import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    arr = np.array(img)
    
    # Save a small version of the entire image to see what it is
    small = img.resize((256, 256), Image.Resampling.LANCZOS)
    small.save("scratch/blonde_eyes_open_small.png")
    
    # Let's count how many non-transparent pixels exist in the entire image
    non_transparent = arr[:,:,3] > 0
    print("Total non-transparent pixels in blonde_eyes_open.png:", np.sum(non_transparent))
    
    y_indices, x_indices = np.where(non_transparent)
    if len(y_indices) > 0:
        print("Y range:", y_indices.min(), "to", y_indices.max())
        print("X range:", x_indices.min(), "to", x_indices.max())
        
if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_eyebrows.png").convert("RGBA")
    arr = np.array(img)
    non_transparent = arr[:,:,3] > 0
    print("Total non-transparent pixels:", np.sum(non_transparent))
    
    y_indices, x_indices = np.where(non_transparent)
    if len(y_indices) > 0:
        print("Eyebrow non-transparent Y range:", y_indices.min(), "to", y_indices.max())
        print("Eyebrow non-transparent X range:", x_indices.min(), "to", x_indices.max())
    else:
        print("No non-transparent pixels found in blonde_eyebrows.png!")

if __name__ == "__main__":
    main()

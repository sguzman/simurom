import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    arr = np.array(img)
    
    # Let's find all non-transparent pixels (alpha > 0)
    y_indices, x_indices = np.where(arr[:,:,3] > 0)
    print("Number of non-transparent pixels:", len(y_indices))
    
    # Print a sample of non-transparent pixels near the boundaries of the non-transparent region
    # (e.g. Y = 500, X around 280-350)
    for x in range(278, 350, 5):
        print(f"At Y=500, X={x}: {arr[500, x]}")
        
    # Let's inspect what's inside blonde_eyebrows.png
    eb = Image.open("assets/mini_game/images/blonde_eyebrows.png").convert("RGBA")
    eb_arr = np.array(eb)
    eb_non_transparent = eb_arr[:,:,3] > 0
    print("Total non-transparent pixels in blonde_eyebrows.png:", np.sum(eb_non_transparent))
    y_eb, x_eb = np.where(eb_non_transparent)
    if len(y_eb) > 0:
        print("Eyebrows Y range:", y_eb.min(), "to", y_eb.max())
        print("Eyebrows X range:", x_eb.min(), "to", x_eb.max())

if __name__ == "__main__":
    main()

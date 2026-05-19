import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/eye-brows.png").convert("RGBA")
    arr = np.array(img)
    
    # We want to key out the white/grey checkerboard.
    # Let's check the checkerboard colors.
    # Typically, the background pixels have R, G, B values very close to each other (grayscale)
    # and they are bright (e.g. > 230).
    # Let's define the mask:
    # A pixel is background if R > 230 and G > 230 and B > 230 and abs(R-G) < 10 and abs(G-B) < 10
    r = arr[:,:,0].astype(int)
    g = arr[:,:,1].astype(int)
    b = arr[:,:,2].astype(int)
    
    is_bg = (r > 220) & (g > 220) & (b > 220) & (np.abs(r - g) < 15) & (np.abs(g - b) < 15)
    
    # Let's set alpha to 0 for background pixels
    arr[is_bg, 3] = 0
    
    keyed_img = Image.fromarray(arr)
    keyed_img.save("assets/mini_game/images/blonde_eyebrows.png")
    
    non_transparent = arr[:,:,3] > 0
    print("Non-transparent pixels after keying:", np.sum(non_transparent))
    
    y_indices, x_indices = np.where(non_transparent)
    if len(y_indices) > 0:
        print("Keyed eyebrows Y range:", y_indices.min(), "to", y_indices.max())
        print("Keyed eyebrows X range:", x_indices.min(), "to", x_indices.max())
        crop = keyed_img.crop((x_indices.min()-10, y_indices.min()-10, x_indices.max()+10, y_indices.max()+10))
        crop.save("scratch/inspect_keyed_brows.png")
        print("Saved keyed brows crop to scratch/inspect_keyed_brows.png")
    else:
        print("No pixels remaining!")

if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr = np.array(img)
    
    # Let's inspect the bounding box of non-transparent pixels in Y in [100, 350], X in [500, 720]
    region = arr[100:350, 500:720]
    h, w = region.shape[:2]
    
    # Let's find pixels that are not fully transparent and print their colors
    # We can cluster colors or just print some stats
    print("Region shape:", region.shape)
    opaque_pixels = region[region[:,:,3] > 0]
    print("Opaque pixels count:", len(opaque_pixels))
    
    # Print a few samples of the colors
    unique_colors, counts = np.unique(opaque_pixels.reshape(-1, 4), axis=0, return_counts=True)
    sorted_indices = np.argsort(-counts)
    
    print("Top 10 most common colors in face region (R, G, B, A) and count:")
    for idx in sorted_indices[:20]:
        print(f"Color: {unique_colors[idx]}, Count: {counts[idx]}")

if __name__ == "__main__":
    main()

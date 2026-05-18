import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/eye-brows.png").convert("RGBA")
    arr = np.array(img)
    
    non_transparent = arr[:,:,3] > 0
    print("Non-transparent pixels in tmp/eye-brows.png:", np.sum(non_transparent))
    
    # Let's count how many pixels are not white/grey
    # Checkerboard is typically close to white/grey
    # Eyebrows are typically brown/black
    # Let's check pixel values that are dark
    dark_pixels = (arr[:,:,0] < 200) & (arr[:,:,3] > 0)
    print("Dark pixels in tmp/eye-brows.png:", np.sum(dark_pixels))
    
    # Save a cropped region of eyebrows to see what is there
    # Let's find the bounding box of dark pixels
    y_indices, x_indices = np.where(dark_pixels)
    if len(y_indices) > 0:
        print("Dark pixels Y range:", y_indices.min(), "to", y_indices.max())
        print("Dark pixels X range:", x_indices.min(), "to", x_indices.max())
        crop = img.crop((x_indices.min()-10, y_indices.min()-10, x_indices.max()+10, y_indices.max()+10))
        crop.save("scratch/inspect_raw_brows_cropped.png")
        print("Saved raw brows crop to scratch/inspect_raw_brows_cropped.png")
    else:
        print("No dark pixels found!")

if __name__ == "__main__":
    main()

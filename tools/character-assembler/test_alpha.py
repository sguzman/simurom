import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/hair.png").convert("RGBA")
    arr = np.array(img)
    print("hair.png shape:", arr.shape)
    print("hair.png max alpha:", arr[:, :, 3].max())
    
    # Let's see what resize does
    resized = img.resize((677, 677), Image.Resampling.BILINEAR)
    r_arr = np.array(resized)
    print("resized shape:", r_arr.shape)
    print("resized max alpha:", r_arr[:, :, 3].max())

if __name__ == "__main__":
    main()

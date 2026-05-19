import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    arr = np.array(img)
    
    # Check non-transparent pixels in Y: 520 to 580, X: 400 to 800
    sub_arr = arr[520:580, 400:800, 3]
    non_transparent_count = np.sum(sub_arr > 0)
    print("Non-transparent pixels in Y [520, 580], X [400, 800]:", non_transparent_count)
    
    # Let's save a crop of this region to see what is drawn there!
    crop = img.crop((400, 520, 800, 580))
    crop.save("scratch/inspect_eyes_raw_upper.png")
    
    # Let's also check if there is an off-white background in the eyes image
    # that was NOT keyed out because it has brightness < 240!
    # Let's print unique RGBA values in a region that should be transparent background
    # (e.g. Y: 530, X: 450)
    print("Pixel at Y=530, X=450:", arr[530, 450])
    print("Pixel at Y=500, X=400:", arr[500, 400])

if __name__ == "__main__":
    main()

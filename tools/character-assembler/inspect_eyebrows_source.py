import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/eye-brows.png").convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # Let's find all non-white pixels
    non_white = (arr[:,:,0] < 254) | (arr[:,:,1] < 254) | (arr[:,:,2] < 254)
    
    # Let's save an image that highlights all non-white pixels in red
    highlight = np.zeros((h, w, 4), dtype=np.uint8)
    highlight[non_white] = [255, 0, 0, 255]
    highlight[~non_white] = [255, 255, 255, 255]
    
    Image.fromarray(highlight).save("scratch/eyebrows_nonwhite_highlight.png")
    
    # Also save a crop of this around the forehead: X: 450 to 800, Y: 100 to 450
    head_crop = Image.fromarray(highlight).crop((450, 100, 800, 450))
    head_crop.save("scratch/eyebrows_nonwhite_head.png")
    
    print("Saved highlights of non-white pixels to scratch/eyebrows_nonwhite_*.png")

if __name__ == "__main__":
    main()

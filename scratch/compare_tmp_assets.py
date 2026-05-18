import numpy as np
from PIL import Image

def main():
    img1 = Image.open("tmp/base-no-eyes.png").convert("RGBA")
    img2 = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    diff = np.abs(arr1.astype(float) - arr2.astype(float))
    print("Base-no-eyes vs blonde_base pixel diff sum:", diff.sum())
    
    img3 = Image.open("tmp/eyes-open.png").convert("RGBA")
    img4 = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    arr3 = np.array(img3)
    arr4 = np.array(img4)
    
    diff2 = np.abs(arr3.astype(float) - arr4.astype(float))
    print("eyes-open vs blonde_eyes_open pixel diff sum:", diff2.sum())

if __name__ == "__main__":
    main()

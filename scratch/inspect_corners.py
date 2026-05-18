import numpy as np
from PIL import Image

def print_pixels(path):
    img = Image.open(path)
    arr = np.array(img)
    print(f"--- Top-left 10x10 block of {path} ---")
    for y in range(10):
        row = []
        for x in range(10):
            pixel = arr[y, x]
            row.append(f"({pixel[0]},{pixel[1]},{pixel[2]})")
        print(" ".join(row))

print_pixels("tmp/hair.png")
print_pixels("tmp/base-no-hair-eyes.png")

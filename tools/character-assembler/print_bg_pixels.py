import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/base-no-hair-eyes.png").convert("RGB")
    arr = np.array(img)
    # Print a 20x20 region from the top-left corner
    print("Top-left 20x20 pixels:")
    for r in range(20):
        row_str = " ".join([f"[{arr[r, c, 0]},{arr[r, c, 1]},{arr[r, c, 2]}]" for c in range(10)])
        print(row_str)

if __name__ == "__main__":
    main()

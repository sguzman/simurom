import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/base-no-hair-eyes.png").convert("RGB")
    arr = np.array(img)
    print("Vertical column at x=100 from y=0 to y=100:")
    for r in range(100):
        if r % 10 == 0:
            print(f"y={r:02d}: {arr[r, 100]}")

if __name__ == "__main__":
    main()

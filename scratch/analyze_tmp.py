import numpy as np
from PIL import Image

def main():
    for name in ["base-no-eyes.png", "eyes-open.png", "eyes-closed.png", "eyes-partial1.png", "eyes-partial2.png", "eyes-partial3.png"]:
        path = f"tmp/{name}"
        try:
            img = Image.open(path).convert("RGBA")
            arr = np.array(img)
            # Find non-white pixels (since they are RGB on white background)
            # A pixel is white if R > 240, G > 240, B > 240
            non_white = np.argwhere((arr[:,:,0] <= 240) | (arr[:,:,1] <= 240) | (arr[:,:,2] <= 240))
            if len(non_white) > 0:
                print(f"{name} non-white box: Y={non_white.min(axis=0)[0]}:{non_white.max(axis=0)[0]}, X={non_white.min(axis=0)[1]}:{non_white.max(axis=0)[1]}")
            else:
                print(f"{name} has no non-white pixels!")
        except Exception as e:
            print(f"Failed to read {name}: {e}")

if __name__ == "__main__":
    main()

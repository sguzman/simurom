import numpy as np
from PIL import Image

def find_bounding_box(path):
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    mask = (arr[:, :, 0] < 240) | (arr[:, :, 1] < 240) | (arr[:, :, 2] < 240)
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    print(f"{path}: Y-range [{rmin}, {rmax}], X-range [{cmin}, {cmax}], Center X: {(cmin+cmax)/2}, Center Y: {(rmin+rmax)/2}")

find_bounding_box("tmp/hair.png")
find_bounding_box("tmp/base-no-hair-eyes.png")

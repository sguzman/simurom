import numpy as np
from PIL import Image

def find_bounding_box(path):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    mask = arr[:, :, 3] > 0
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    print(f"{path}: Y-range [{rmin}, rmax={rmax}], X-range [{cmin}, cmax={cmax}], Center X: {(cmin+cmax)/2}, Center Y: {(rmin+rmax)/2}")

find_bounding_box("assets/mini_game/images/blonde_base.png")

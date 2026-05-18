import numpy as np
from PIL import Image

def get_bbox_dims(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    # Check if transparent or needs white keying
    mask = (arr[:, :, 3] > 0) & ~((arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240))
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    ymin, ymax = ys.min(), ys.max()
    xmin, xmax = xs.min(), xs.max()
    return (xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)

def main():
    base_full = get_bbox_dims("tmp/base.png")
    base_no_hair = get_bbox_dims("tmp/base-no-hair-eyes.png")
    hair = get_bbox_dims("tmp/hair.png")
    
    print(f"base.png BBox: {base_full}")
    print(f"base-no-hair-eyes.png BBox: {base_no_hair}")
    print(f"hair.png BBox: {hair}")

if __name__ == "__main__":
    main()

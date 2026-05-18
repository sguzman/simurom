import numpy as np
from PIL import Image

def get_bbox(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    non_white = (arr[:,:,0] < 240) | (arr[:,:,1] < 240) | (arr[:,:,2] < 240)
    y_indices, x_indices = np.where(non_white)
    if len(y_indices) > 0:
        return {
            "ymin": y_indices.min(), "ymax": y_indices.max(), "ycenter": np.mean(y_indices),
            "xmin": x_indices.min(), "xmax": x_indices.max(), "xcenter": np.mean(x_indices),
            "count": len(y_indices)
        }
    return None

def main():
    eyes = get_bbox("tmp/eyes-open.png")
    brows = get_bbox("tmp/eye-brows.png")
    
    print("Eyes bbox:", eyes)
    print("Brows bbox:", brows)

if __name__ == "__main__":
    main()

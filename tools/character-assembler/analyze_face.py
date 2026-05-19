import numpy as np
from PIL import Image

def main():
    img_b = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr_b = np.array(img_b)
    h, w = arr_b.shape[:2]
    
    opaque_y, opaque_x = np.where(arr_b[:,:,3] > 0)
    print("Opaque body bounds:")
    print("Y:", opaque_y.min(), "to", opaque_y.max())
    print("X:", opaque_x.min(), "to", opaque_x.max())
    
    # Let's crop the head region
    # The head starts at opaque_y.min() (around 29)
    # Let's crop a window of 300x300 around the top center of the body
    head_top = opaque_y.min()
    body_center_x = int(np.median(opaque_x))
    
    # We want to crop from head_top to head_top + 300, and body_center_x - 200 to body_center_x + 200
    head_y_start = head_top
    head_y_end = head_top + 300
    head_x_start = body_center_x - 200
    head_x_end = body_center_x + 200
    
    print(f"Head crop region: Y={head_y_start}:{head_y_end}, X={head_x_start}:{head_x_end}")
    
    head_crop = arr_b[head_y_start:head_y_end, head_x_start:head_x_end]
    Image.fromarray(head_crop).save("scratch/head_crop.png")
    print("Saved scratch/head_crop.png")

if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def key_out_white_smart(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    out_arr = arr.copy()
    for y in range(h):
        for x in range(w):
            r, g, b, a = arr[y, x]
            if r > 180 and g > 180 and b > 180:
                brightness = (int(r) + int(g) + int(b)) / 3.0
                if brightness >= 254:
                    out_arr[y, x, 3] = 0
                else:
                    alpha_factor = (254.0 - brightness) / (254.0 - 180.0)
                    alpha_factor = max(0.0, min(1.0, alpha_factor))
                    out_arr[y, x, 3] = int(255 * alpha_factor)
                    for c in range(3):
                        c_blended = arr[y, x, c]
                        unblended = (c_blended - 255 * (1.0 - alpha_factor)) / (alpha_factor + 1e-5)
                        out_arr[y, x, c] = int(max(0.0, min(255.0, unblended)))
            
    return Image.fromarray(out_arr)

def main():
    cleaned_brows = key_out_white_smart("tmp/eye-brows.png")
    cleaned_brows.save("assets/mini_game/images/blonde_eyebrows.png")
    print("Successfully processed and saved transparent eyebrows to assets/mini_game/images/blonde_eyebrows.png")

if __name__ == "__main__":
    main()

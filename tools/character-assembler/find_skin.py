import numpy as np
from PIL import Image

def main():
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # We scan the upper half Y in 0:400, X in 400:850
    # Let's search for flesh tones: R > 200, 140 < G < 210, 100 < B < 180, A > 0
    flesh_y, flesh_x = np.where(
        (arr[:400, 400:850, 0] > 200) &
        (arr[:400, 400:850, 1] > 140) & (arr[:400, 400:850, 1] < 210) &
        (arr[:400, 400:850, 2] > 100) & (arr[:400, 400:850, 2] < 185) &
        (arr[:400, 400:850, 3] > 0)
    )
    
    if len(flesh_y) > 0:
        actual_flesh_y = flesh_y + 0
        actual_flesh_x = flesh_x + 400
        print("Flesh/Face bounds inside blonde_base.png:")
        print(f"Y: {actual_flesh_y.min()} to {actual_flesh_y.max()} (Height: {actual_flesh_y.max() - actual_flesh_y.min() + 1})")
        print(f"X: {actual_flesh_x.min()} to {actual_flesh_x.max()} (Width: {actual_flesh_x.max() - actual_flesh_x.min() + 1})")
        print(f"Center: Y={int(np.mean(actual_flesh_y))}, X={int(np.mean(actual_flesh_x))}")
    else:
        print("No flesh tones found in the specified head area!")

if __name__ == "__main__":
    main()

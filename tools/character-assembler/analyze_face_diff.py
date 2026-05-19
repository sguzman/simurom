import numpy as np
from PIL import Image

def main():
    img_with = Image.open("tmp/base.png").convert("RGBA")
    img_without = Image.open("tmp/base-no-eyes.png").convert("RGBA")
    
    arr_with = np.array(img_with)[100:300, 500:720]
    arr_without = np.array(img_without)[100:300, 500:720]
    
    # Calculate pixel difference in this region
    diff = np.abs(arr_with.astype(float) - arr_without.astype(float))
    diff_sum = diff.sum(axis=2)
    
    # Print statistics of the differences
    print("Max diff in face region:", diff_sum.max())
    print("Mean diff in face region:", diff_sum.mean())
    
    # Find coordinates of the largest differences
    y_indices, x_indices = np.where(diff_sum > 50)
    if len(y_indices) > 0:
        actual_y = y_indices + 100
        actual_x = x_indices + 500
        print("Diff bounds in face region:")
        print(f"Y bounds: {actual_y.min()} to {actual_y.max()}")
        print(f"X bounds: {actual_x.min()} to {actual_x.max()}")
        print(f"Center: Y={int(np.mean(actual_y))}, X={int(np.mean(actual_x))}")
    else:
        print("No significant difference in face region!")

if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def analyze_image(path):
    img = Image.open(path)
    arr = np.array(img)
    print(f"--- Analysis for {path} ---")
    print(f"Shape: {arr.shape}")
    print(f"Modes: {img.mode}")
    
    # Check transparency
    if arr.shape[2] == 4:
        alpha = arr[:, :, 3]
        total_pixels = alpha.size
        opaque_pixels = np.sum(alpha == 255)
        transparent_pixels = np.sum(alpha == 0)
        semi_pixels = total_pixels - opaque_pixels - transparent_pixels
        print(f"Opaque pixels: {opaque_pixels} ({opaque_pixels/total_pixels:.2%})")
        print(f"Fully transparent pixels: {transparent_pixels} ({transparent_pixels/total_pixels:.2%})")
        print(f"Semi-transparent pixels: {semi_pixels} ({semi_pixels/total_pixels:.2%})")
    else:
        print("No alpha channel present")
        
    # Check corner pixels
    corners = [(0, 0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)]
    for cx, cy in corners:
        print(f"Corner ({cx}, {cy}): {arr[cy, cx]}")

analyze_image("tmp/hair.png")
analyze_image("tmp/base-no-hair-eyes.png")

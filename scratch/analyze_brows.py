import numpy as np
from PIL import Image

def main():
    img = Image.open("tmp/eye-brows.png").convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    print(f"Image dimensions: {w}x{h}")
    
    # Find non-white pixels
    non_white = (arr[:,:,0] < 240) | (arr[:,:,1] < 240) | (arr[:,:,2] < 240)
    y_indices, x_indices = np.where(non_white)
    
    if len(y_indices) > 0:
        print(f"Non-white pixels bounding box:")
        print(f"Y: {y_indices.min()} to {y_indices.max()} (center: {np.mean(y_indices):.2f})")
        print(f"X: {x_indices.min()} to {x_indices.max()} (center: {np.mean(x_indices):.2f})")
        print(f"Total non-white pixels: {len(y_indices)}")
        
        # Let's inspect some sample pixels in that region
        region_y = int(np.mean(y_indices))
        region_x = int(np.mean(x_indices))
        print(f"Sample color near center ({region_x}, {region_y}):", arr[region_y, region_x])
    else:
        print("No non-white pixels found!")

if __name__ == "__main__":
    main()

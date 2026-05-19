import numpy as np
from PIL import Image

def main():
    img_with = Image.open("tmp/base.png").convert("RGBA")
    img_without = Image.open("tmp/base-no-eyes.png").convert("RGBA")
    
    arr_with = np.array(img_with)
    arr_without = np.array(img_without)
    
    # Find all pixels where they differ
    # We allow a small tolerance since there could be compression artifacts or minor differences
    diff_mask = np.any(np.abs(arr_with.astype(float) - arr_without.astype(float)) > 10, axis=2)
    
    diff_y, diff_x = np.where(diff_mask)
    
    if len(diff_y) > 0:
        print("Differences between base.png and base-no-eyes.png (the eyes on the face):")
        print(f"Y bounds: {diff_y.min()} to {diff_y.max()} (Height: {diff_y.max() - diff_y.min() + 1})")
        print(f"X bounds: {diff_x.min()} to {diff_x.max()} (Width: {diff_x.max() - diff_x.min() + 1})")
        print(f"Center: Y={int(np.mean(diff_y))}, X={int(np.mean(diff_x))}")
        
        # Let's save a crop of this difference region from both images
        crop_box = (diff_x.min() - 20, diff_y.min() - 20, diff_x.max() + 20, diff_y.max() + 20)
        img_with.crop(crop_box).save("scratch/eye_place_with.png")
        img_without.crop(crop_box).save("scratch/eye_place_without.png")
        print("Saved crop previews to scratch/eye_place_*.png!")
    else:
        print("No differences found between base.png and base-no-eyes.png!")

if __name__ == "__main__":
    main()

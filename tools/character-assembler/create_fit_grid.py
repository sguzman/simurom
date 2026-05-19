import os
from PIL import Image, ImageDraw, ImageFont

def main():
    scales = [0.16, 0.18, 0.20, 0.22]
    y_centers = [150, 160, 170, 180, 190]
    
    # We will create a grid of 4 columns (scales) and 5 rows (y_centers)
    # Each cell is 300x300 pixels
    grid_img = Image.new("RGBA", (4 * 300, 5 * 300), (255, 255, 255, 255))
    draw = ImageDraw.Draw(grid_img)
    
    for c_idx, scale in enumerate(scales):
        for r_idx, y_center in enumerate(y_centers):
            path = f"scratch/fit/scale_{scale:.2f}_y_{y_center}.png"
            if os.path.exists(path):
                cell_img = Image.open(path).convert("RGBA")
                grid_img.paste(cell_img, (c_idx * 300, r_idx * 300))
                # Draw text label
                draw.text((c_idx * 300 + 10, r_idx * 300 + 10), f"S={scale:.2f} Y={y_center}", fill=(255, 0, 0, 255))
                
    grid_img.save("scratch/fit_grid.png")
    print("Saved scratch/fit_grid.png!")

if __name__ == "__main__":
    main()

from PIL import Image, ImageDraw, ImageFont

def main():
    # Load base image
    img = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    
    # We want to crop from Y=0 to Y=500, X=350 to X=850
    crop_y0, crop_y1 = 0, 500
    crop_x0, crop_x1 = 350, 850
    
    cropped = img.crop((crop_x0, crop_y0, crop_x1, crop_y1))
    draw = ImageDraw.Draw(cropped)
    
    # Draw horizontal grid lines every 20 pixels
    for y in range(0, 500, 20):
        actual_y = crop_y0 + y
        draw.line([(0, y), (500, y)], fill=(255, 0, 0, 100), width=1)
        draw.text((5, y + 2), f"Y={actual_y}", fill=(255, 0, 0, 255))
        
    # Draw vertical grid lines every 20 pixels
    for x in range(0, 500, 20):
        actual_x = crop_x0 + x
        draw.line([(x, 0), (x, 500)], fill=(0, 0, 255, 100), width=1)
        draw.text((x + 2, 5), f"X={actual_x}", fill=(0, 0, 255, 255))
        
    cropped.save("scratch/head_grid.png")
    print("Saved scratch/head_grid.png with coordinate grid!")

if __name__ == "__main__":
    main()

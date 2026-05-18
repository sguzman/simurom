import os
from PIL import Image

def main():
    gif = Image.open("artifacts/blonde_blinking.gif")
    os.makedirs("scratch/gif_frames", exist_ok=True)
    
    # Save the first 3 frames as PNG
    for i in range(min(5, gif.n_frames)):
        gif.seek(i)
        frame = gif.convert("RGBA")
        frame.save(f"scratch/gif_frames/frame_{i}.png")
        # Crop head region: X: 450 to 800, Y: 100 to 450
        crop = frame.crop((450, 100, 800, 450))
        crop.save(f"scratch/gif_frames/head_{i}.png")
        
    print(f"Saved first few frames and head crops to scratch/gif_frames/")

if __name__ == "__main__":
    main()

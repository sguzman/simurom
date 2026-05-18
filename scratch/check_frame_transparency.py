from PIL import Image

def main():
    img = Image.open("scratch/gif_frames/frame_0.png")
    print("Format:", img.format)
    print("Mode:", img.mode)
    print("Size:", img.size)
    
    # Check if there is any alpha channel < 255
    alphas = [pixel[3] for pixel in img.getdata()]
    transparent_count = sum(1 for a in alphas if a < 255)
    print("Total pixels:", len(alphas))
    print("Transparent/semi-transparent pixels:", transparent_count)

if __name__ == "__main__":
    main()

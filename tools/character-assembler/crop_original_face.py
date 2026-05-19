from PIL import Image

def main():
    img = Image.open("tmp/base.png")
    # Crop head region: X: 450 to 800, Y: 100 to 450
    head = img.crop((450, 100, 800, 450))
    head.save("scratch/head_original.png")
    print("Saved original head crop to scratch/head_original.png")

if __name__ == "__main__":
    main()

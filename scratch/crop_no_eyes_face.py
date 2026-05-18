from PIL import Image

def main():
    img = Image.open("tmp/base-no-eyes.png")
    head = img.crop((450, 100, 800, 450))
    head.save("scratch/head_no_eyes.png")
    print("Saved no-eyes head crop to scratch/head_no_eyes.png")

if __name__ == "__main__":
    main()

from PIL import Image

def main():
    img1 = Image.open("tmp/base.png")
    img2 = Image.open("tmp/base-no-hair-eyes.png")
    img3 = Image.open("tmp/hair.png")
    print(f"base.png size: {img1.size}")
    print(f"base-no-hair-eyes.png size: {img2.size}")
    print(f"hair.png size: {img3.size}")

if __name__ == "__main__":
    main()

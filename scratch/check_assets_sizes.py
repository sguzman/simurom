import os
from PIL import Image

def main():
    folder = "assets/mini_game/images"
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            path = os.path.join(folder, filename)
            img = Image.open(path)
            print(f"{filename}: size={img.size}, mode={img.mode}")

if __name__ == "__main__":
    main()

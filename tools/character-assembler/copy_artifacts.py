import shutil
import os

def main():
    dest_dir = "/home/admin/.gemini/antigravity/brain/7c8dab13-650c-4f8b-8ff3-3a5aa8950c2e"
    os.makedirs(dest_dir, exist_ok=True)
    
    shutil.copy("blonde_preview.png", os.path.join(dest_dir, "blonde_preview.png"))
    shutil.copy("blonde_blinking.gif", os.path.join(dest_dir, "blonde_blinking.gif"))
    
    print("Successfully copied blonde_preview.png and blonde_blinking.gif to brain artifacts!")

if __name__ == "__main__":
    main()

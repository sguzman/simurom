import numpy as np
from PIL import Image

def main():
    # Load the processed eyebrows
    eyebrows = Image.open("assets/mini_game/images/blonde_eyebrows.png").convert("RGBA")
    eb_arr = np.array(eyebrows)
    non_transparent_eb = eb_arr[:,:,3] > 0
    print("Non-transparent pixels in blonde_eyebrows.png:", np.sum(non_transparent_eb))
    
    # Load frame 0 of the GIF
    frame = Image.open("scratch/gif_frames/frame_0.png").convert("RGBA")
    fr_arr = np.array(frame)
    
    # Load the static preview PNG
    preview = Image.open("artifacts/blonde_preview.png").convert("RGBA")
    pr_arr = np.array(preview)
    
    # Let's compare frame 0 of the GIF and the static preview PNG!
    # Are they identical?
    diff = np.abs(fr_arr.astype(int) - pr_arr.astype(int))
    max_diff = diff.max()
    mean_diff = diff.mean()
    print("Max difference between GIF frame 0 and static preview PNG:", max_diff)
    print("Mean difference between GIF frame 0 and static preview PNG:", mean_diff)
    
    # Let's save a diff image
    diff_img = Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8))
    diff_img.save("scratch/gif_vs_png_diff.png")
    
    # Let's check if the eyebrows are actually present in BOTH or NEITHER!
    # Let's crop the eye/eyebrow region in the static preview: X: 550 to 700, Y: 200 to 300
    crop_pr = preview.crop((550, 200, 700, 300))
    crop_pr.save("scratch/inspect_preview_forehead.png")
    
    crop_fr = frame.crop((550, 200, 700, 300))
    crop_fr.save("scratch/inspect_gif_forehead.png")
    
    print("Saved forehead inspections to scratch/inspect_*_forehead.png")

if __name__ == "__main__":
    main()

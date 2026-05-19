import os
from PIL import Image

def main():
    frames_paths = [
        "assets/mini_game/images/blonde_eyes_open.png",
        "assets/mini_game/images/blonde_eyes_partial1.png",
        "assets/mini_game/images/blonde_eyes_partial2.png",
        "assets/mini_game/images/blonde_eyes_partial3.png",
        "assets/mini_game/images/blonde_eyes_closed.png"
    ]
    
    # Combined Union BBox: X [269, 984], Y [482, 728]
    # Let's add a small padding of 10 pixels around the eyes to make it look clean
    pad = 10
    min_x = max(0, 269 - pad)
    max_x = min(1254, 984 + pad)
    min_y = max(0, 482 - pad)
    max_y = min(1254, 728 + pad)
    
    bbox = (min_x, min_y, max_x, max_y)
    
    # Load and crop frames
    cropped_frames = []
    for path in frames_paths:
        img = Image.open(path).convert("RGBA")
        cropped = img.crop(bbox)
        cropped_frames.append(cropped)
        
    # Save static preview
    static_preview = cropped_frames[0]
    output_png = "/home/admin/.gemini/antigravity/brain/7c8dab13-650c-4f8b-8ff3-3a5aa8950c2e/eyes_preview.png"
    static_preview.save(output_png, "PNG")
    print(f"Saved static preview to {output_png}")
    
    # Build dynamic blinking loop sequence (45 frames total)
    # open -> partial1 -> partial2 -> partial3 -> closed -> partial3 -> partial2 -> partial1 -> open...
    sequence_indices = [
        0, # open
        1, # partial1
        2, # partial2
        3, # partial3
        4, # closed
        3, # partial3
        2, # partial2
        1  # partial1
    ]
    # Append 37 open frames to create a natural open eyes delay
    sequence_indices.extend([0] * 37)
    
    # Build list of PIL Images for the GIF
    gif_images = []
    for idx in sequence_indices:
        # Convert RGBA to P (palette mode) with transparency preserved
        rgba_img = cropped_frames[idx]
        
        # To maintain high-fidelity colors and clean transparency, we map to adaptive palette
        # and preserve the transparent mask
        alpha = rgba_img.split()[3]
        
        # Convert RGB part to Palette mode
        rgb_img = rgba_img.convert("RGB")
        p_img = rgb_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
        
        # Find a color index that is not used or designate index 255 as transparent
        mask = Image.eval(alpha, lambda a: 255 if a < 128 else 0)
        p_img.paste(255, mask)
        p_img.info['transparency'] = 255
        
        gif_images.append(p_img)
        
    output_gif = "/home/admin/.gemini/antigravity/brain/7c8dab13-650c-4f8b-8ff3-3a5aa8950c2e/eyes_blinking.gif"
    
    # Save animated GIF
    gif_images[0].save(
        output_gif,
        save_all=True,
        append_images=gif_images[1:],
        duration=50, # 50 ms per frame
        loop=0,      # Loop infinitely
        disposal=2,  # Clear frame background to prevent ghosting
        transparency=255
    )
    print(f"Saved animated blinking eyes GIF to {output_gif}")

if __name__ == "__main__":
    main()

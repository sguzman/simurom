import numpy as np
from PIL import Image

def key_out_white_smart(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    
    # Let's inspect the eyebrow colors and white background colors.
    # The background is extremely white: R=255, G=255, B=255.
    # Let's do a soft keying based on the minimum difference to white (255, 255, 255)
    # For each pixel, if R > 200 and G > 200 and B > 200:
    # we can compute alpha.
    out_arr = arr.copy()
    for y in range(h):
        for x in range(w):
            r, g, b, a = arr[y, x]
            # Calculate distance to white
            if r > 180 and g > 180 and b > 180:
                # This is a background or fringe pixel.
                # Let's calculate its alpha based on how far it is from white (255, 255, 255)
                # If we assume eyebrow color is around R=100, G=70, B=50
                # Let's just set alpha proportional to the distance from white:
                # For example, if it's pure white, alpha = 0.
                # If it's darker, alpha increases.
                brightness = (int(r) + int(g) + int(b)) / 3.0
                if brightness >= 254:
                    out_arr[y, x, 3] = 0
                else:
                    # Map [180, 254] to alpha [255, 0]
                    alpha_factor = (254.0 - brightness) / (254.0 - 180.0)
                    alpha_factor = max(0.0, min(1.0, alpha_factor))
                    out_arr[y, x, 3] = int(255 * alpha_factor)
                    # Also, adjust the RGB channels to remove the white color bleeding:
                    # C_unblended = (C_blended - 255 * (1 - alpha)) / alpha
                    # Let's clamp it to avoid negative values
                    for c in range(3):
                        c_blended = arr[y, x, c]
                        unblended = (c_blended - 255 * (1.0 - alpha_factor)) / (alpha_factor + 1e-5)
                        out_arr[y, x, c] = int(max(0.0, min(255.0, unblended)))
            
    return Image.fromarray(out_arr)

def main():
    base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    eyes_raw = Image.open("assets/mini_game/images/blonde_eyes_open.png").convert("RGBA")
    
    # Process eyebrows
    brows = key_out_white_smart("tmp/eye-brows.png")
    brows.save("scratch/blonde_eyebrows_clean.png")
    
    # Paste eyes: scale = 0.2225, rotation = 10.25, cx = 607.4, cy = 264.0
    eye_scale = 0.2225
    eye_angle = 10.25
    eye_cx = 607.4
    eye_cy = 264.0
    
    eyes_crop = eyes_raw.crop((278, 482, 973, 717))
    w_new = int((973 - 278) * eye_scale)
    h_new = int((717 - 482) * eye_scale)
    eyes_resized = eyes_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    eyes_rotated = eyes_resized.rotate(eye_angle, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = eyes_rotated.size
    
    x_left = int(eye_cx - w_rot / 2)
    y_top = int(eye_cy - h_rot / 2)
    
    composite = base.copy()
    composite.paste(eyes_rotated, (x_left, y_top), eyes_rotated)
    
    # Paste brows: scale = 0.2400, rotation = 10.25, cx = 602.0, cy = 247.0
    brow_scale = 0.2400
    brow_angle = 10.25
    brow_cx = 602.0
    brow_cy = 247.0
    
    brows_crop = brows.crop((301, 580, 952, 655))
    w_new = int((952 - 301) * brow_scale)
    h_new = int((655 - 580) * brow_scale)
    brows_resized = brows_crop.resize((w_new, h_new), Image.Resampling.LANCZOS)
    brows_rotated = brows_resized.rotate(brow_angle, Image.Resampling.BICUBIC, expand=True)
    w_rot, h_rot = brows_rotated.size
    
    x_left = int(brow_cx - w_rot / 2)
    y_top = int(brow_cy - h_rot / 2)
    
    composite.paste(brows_rotated, (x_left, y_top), brows_rotated)
    composite.save("scratch/composite_with_brows_clean.png")
    
    # Crop head
    head = composite.crop((450, 100, 800, 450))
    head.save("scratch/head_with_brows_clean.png")
    print("Saved clean preview to scratch/head_with_brows_clean.png")

if __name__ == "__main__":
    main()

import numpy as np
from PIL import Image

def transform_layer_pil(img, s, ox, oy):
    w, h = img.size
    new_w = int(round(w * s))
    new_h = int(round(h * s))
    
    # Scale hair
    scaled = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    # Centered position
    left = (1254 - new_w) / 2.0
    top = (1254 - new_h) / 2.0
    
    # Add translation (shift ox to right, shift oy UP which is negative Y in PIL)
    left_shifted = left + ox
    top_shifted = top - oy
    
    # Create blank canvas
    canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
    canvas.paste(scaled, (int(round(left_shifted)), int(round(top_shifted))), scaled)
    return canvas

def main():
    old_base = Image.open("assets/mini_game/images/blonde_base.png").convert("RGBA")
    new_hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    
    # Key out white background of new_hair
    arr = np.array(new_hair_raw)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    new_hair = Image.fromarray(arr)
    
    # We will generate a grid of test cases
    scales = [1.2, 1.25, 1.3, 1.35]
    x_offsets = [-15, -10, -5]
    y_offsets = [80, 100, 120]
    
    for s in scales:
        for ox in x_offsets:
            for oy in y_offsets:
                transformed_hair = transform_layer_pil(new_hair, s, ox, oy)
                
                # Draw new hair in semi-transparent red on top of old_base
                trans_arr = np.array(transformed_hair)
                non_trans = trans_arr[:, :, 3] > 0
                trans_arr[non_trans] = [255, 0, 0, 120]
                trans_hair_img = Image.fromarray(trans_arr)
                
                composite = old_base.copy()
                composite.paste(trans_hair_img, (0, 0), trans_hair_img)
                composite.crop((350, 50, 900, 600)).save(f"scratch/hair_test_s_{s:.2f}_ox_{ox:.1f}_oy_{oy:.1f}.png")
                
    print("Fast test generation completed successfully!")

if __name__ == "__main__":
    main()

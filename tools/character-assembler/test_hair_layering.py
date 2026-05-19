import numpy as np
from PIL import Image

def simple_key(img):
    arr = np.array(img)
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask, 3] = 0
    return Image.fromarray(arr)

def main():
    # Load raw assets
    base_raw = Image.open("tmp/base-no-hair-eyes.png").convert("RGBA")
    hair_raw = Image.open("tmp/hair.png").convert("RGBA")
    eyes_raw = Image.open("tmp/eyes-open.png").convert("RGBA")
    brows_raw = Image.open("tmp/eye-brows.png").convert("RGBA")
    
    # Key out white backgrounds
    base = simple_key(base_raw)
    hair_unaligned = simple_key(hair_raw)
    eyes = simple_key(eyes_raw)
    brows = simple_key(brows_raw)
    
    # Align hair: scale = 1.25, ox = -5.0, oy = 120.0
    w, h = hair_unaligned.size
    new_w = int(round(w * 1.25))
    new_h = int(round(h * 1.25))
    hair_scaled = hair_unaligned.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    left = int(round((1254 - new_w) / 2.0 - 5.0))
    top = int(round((1254 - new_h) / 2.0 - 120.0))
    
    hair = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
    hair.paste(hair_scaled, (left, top), hair_scaled)
    
    # Align eyes: scale = 0.2225, ox = -19.6, oy = 363.0, rotation = 10.25
    # Align eyebrows: scale = 0.24, ox = -25.0, oy = 410.0, rotation = 10.25
    # Let's use our helper to transform them correctly
    def transform_part(img, s, r, ox, oy):
        # Rotate and scale
        w, h = img.size
        # Pad first to prevent cropping during rotation
        padded = Image.new("RGBA", (w*2, h*2), (0, 0, 0, 0))
        padded.paste(img, (w//2, h//2), img)
        
        rotated = padded.rotate(-r, resample=Image.Resampling.BILINEAR)
        # Bounding box of rotated
        bbox = rotated.getbbox()
        cropped = rotated.crop(bbox)
        
        # Scale
        cw, ch = cropped.size
        scaled_w = int(round(cw * s))
        scaled_h = int(round(ch * s))
        scaled = cropped.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)
        
        # Paste centered on canvas with offsets
        canvas = Image.new("RGBA", (1254, 1254), (0, 0, 0, 0))
        left = int(round((1254 - scaled_w)/2.0 + ox))
        top = int(round((1254 - scaled_h)/2.0 - oy))
        canvas.paste(scaled, (left, top), scaled)
        return canvas
        
    eyes_placed = transform_part(eyes, 0.2225, 10.25, -19.6, 363.0)
    brows_placed = transform_part(brows, 0.24, 10.25, -25.0, 410.0)
    
    # Composite A: Body -> Hair -> Eyes -> Eyebrows (Eyes/Brows on top of hair)
    comp_a = base.copy()
    comp_a.paste(hair, (0, 0), hair)
    comp_a.paste(eyes_placed, (0, 0), eyes_placed)
    comp_a.paste(brows_placed, (0, 0), brows_placed)
    comp_a.save("scratch/composite_hair_under.png")
    
    # Composite B: Body -> Eyes -> Eyebrows -> Hair (Hair on top of eyes/brows)
    comp_b = base.copy()
    comp_b.paste(eyes_placed, (0, 0), eyes_placed)
    comp_b.paste(brows_placed, (0, 0), brows_placed)
    comp_b.paste(hair, (0, 0), hair)
    comp_b.save("scratch/composite_hair_top.png")
    
    print("Generated both composites!")

if __name__ == "__main__":
    main()

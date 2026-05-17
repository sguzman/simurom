#!/usr/bin/env python3
import os
import sys
import argparse
import tomllib
from PIL import Image

def load_character_spec(toml_path):
    with open(toml_path, "rb") as f:
        return tomllib.load(f)

def composite_layers(base_size, layers, assets_dir):
    """
    layers is a list of tuples: (image_path, offset_x, offset_y)
    All layers are blended on top of a transparent base image.
    """
    composite = Image.new("RGBA", base_size, (0, 0, 0, 0))
    for path, ox, oy in layers:
        full_path = os.path.join(assets_dir, path)
        if not os.path.exists(full_path):
            print(f"Warning: Sprite file not found: {full_path}", file=sys.stderr)
            continue
        
        layer_img = Image.open(full_path).convert("RGBA")
        
        # Paste with alpha channel preservation
        if ox == 0 and oy == 0:
            composite = Image.alpha_composite(composite, layer_img)
        else:
            # Create a offset layer
            offset_canvas = Image.new("RGBA", base_size, (0, 0, 0, 0))
            # Shift offset (note: Bevy y-axis is up, PIL y-axis is down, but for simple previews we match standard displacement)
            # Standard offset paste:
            offset_canvas.paste(layer_img, (int(ox), int(-oy)))
            composite = Image.alpha_composite(composite, offset_canvas)
            
    return composite

def main():
    parser = argparse.ArgumentParser(description="Simurom Character Composite Preview Generator")
    parser.add_argument("--character", "-c", required=True, help="Path to character TOML file")
    parser.add_argument("--output-png", "-p", help="Output path for the default composite PNG preview")
    parser.add_argument("--output-gif", "-g", help="Output path for the animated blinking GIF preview")
    parser.add_argument("--assets-dir", "-a", default="assets", help="Path to assets root directory")
    args = parser.parse_args()

    if not os.path.exists(args.character):
        print(f"Error: Character TOML file not found: {args.character}", file=sys.stderr)
        sys.exit(1)

    try:
        spec = load_character_spec(args.character)
    except Exception as e:
        print(f"Error parsing character TOML: {e}", file=sys.stderr)
        sys.exit(1)

    char_cfg = spec.get("character", {})
    segments = char_cfg.get("segments", [])
    scale = char_cfg.get("scale", 1.0)

    # Sort segments by layer_offset (lowest first, so they are rendered bottom-to-top)
    segments.sort(key=lambda s: s.get("layer_offset", 0.0))

    # Determine reference canvas size from first valid segment image
    base_size = (1254, 1254) # Fallback default
    for seg in segments:
        sprite_path = os.path.join(args.assets_dir, seg.get("sprite", ""))
        if os.path.exists(sprite_path):
            with Image.open(sprite_path) as img:
                base_size = img.size
                break

    print(f"Compositing character '{char_cfg.get('name', 'Unnamed')}' with canvas size {base_size}...")

    # 1. Generate Static PNG Preview (using default sprite configurations)
    if args.output_png:
        layers = []
        for seg in segments:
            sprite_path = seg.get("sprite", "")
            offset = seg.get("offset", {"x": 0.0, "y": 0.0})
            layers.append((sprite_path, offset.get("x", 0.0), offset.get("y", 0.0)))
        
        static_img = composite_layers(base_size, layers, args.assets_dir)
        
        # Apply scaling if requested
        if scale != 1.0:
            new_size = (int(base_size[0] * scale), int(base_size[1] * scale))
            static_img = static_img.resize(new_size, Image.Resampling.LANCZOS)

        os.makedirs(os.path.dirname(os.path.abspath(args.output_png)), exist_ok=True)
        static_img.save(args.output_png, "PNG")
        print(f"Successfully generated static preview PNG at: {args.output_png}")

    # 2. Generate Looping GIF Preview for blinking animation behavior
    if args.output_gif:
        # Look for blinking frames in the eyes segment
        blink_frames_paths = []
        eyes_segment_idx = -1
        
        for idx, seg in enumerate(segments):
            blink_cfg = seg.get("blink", {})
            if blink_cfg and "blink_frames" in blink_cfg:
                blink_frames_paths = blink_cfg["blink_frames"]
                eyes_segment_idx = idx
                break

        if not blink_frames_paths:
            # Fallback check if simple closed_sprite is present
            for idx, seg in enumerate(segments):
                blink_cfg = seg.get("blink", {})
                if blink_cfg and "closed_sprite" in blink_cfg:
                    blink_frames_paths = [seg.get("sprite", ""), blink_cfg["closed_sprite"]]
                    eyes_segment_idx = idx
                    break

        if eyes_segment_idx == -1 or not blink_frames_paths:
            print("No blinking segment or frames found in character specification. Skipping GIF generation.", file=sys.stderr)
            sys.exit(0)

        # Build full sequence of eye frames for a single blink loop:
        # open -> partial1 -> partial2 -> partial3 -> closed -> partial3 -> partial2 -> partial1 -> open
        # Then append some open frames to simulate the idle duration between blinks!
        
        # Build the active blink sequence
        active_sequence = list(blink_frames_paths)
        # Add reverse frames (excluding the fully closed last frame and fully open first frame to avoid double frames)
        reverse_sequence = list(reversed(blink_frames_paths[1:-1]))
        full_blink_sequence = active_sequence + reverse_sequence
        
        # Create a series of frames
        gif_frames = []
        
        # We'll generate 40 frames total:
        # - The blink transition sequence (e.g. 9 frames)
        # - Followed by 31 frames of fully open/idle state (so the blink is quick and realistic!)
        total_gif_frames_count = 45
        
        # Parse timing details
        frame_dur_seconds = float(spec.get("character", {}).get("segments", [])[eyes_segment_idx].get("blink", {}).get("frame_duration", 0.05))
        frame_dur_ms = int(frame_dur_seconds * 1000)
        
        for i in range(total_gif_frames_count):
            # Determine which eye sprite to overlay
            if i < len(full_blink_sequence):
                current_eye_sprite = full_blink_sequence[i]
            else:
                current_eye_sprite = blink_frames_paths[0] # Fully open/default
            
            # Composite all segments, substituting the eye segment with the current_eye_sprite
            layers = []
            for idx, seg in enumerate(segments):
                offset = seg.get("offset", {"x": 0.0, "y": 0.0})
                if idx == eyes_segment_idx:
                    sprite_path = current_eye_sprite
                else:
                    sprite_path = seg.get("sprite", "")
                
                layers.append((sprite_path, offset.get("x", 0.0), offset.get("y", 0.0)))
            
            frame_img = composite_layers(base_size, layers, args.assets_dir)
            if scale != 1.0:
                new_size = (int(base_size[0] * scale), int(base_size[1] * scale))
                frame_img = frame_img.resize(new_size, Image.Resampling.LANCZOS)
                
            gif_frames.append(frame_img)

        # Save as animated looping GIF
        os.makedirs(os.path.dirname(os.path.abspath(args.output_gif)), exist_ok=True)
        # Save first frame and append remaining
        gif_frames[0].save(
            args.output_gif,
            save_all=True,
            append_images=gif_frames[1:],
            duration=frame_dur_ms,
            loop=0,
            optimize=True
        )
        print(f"Successfully generated dynamic blinking animated GIF at: {args.output_gif}")

if __name__ == "__main__":
    main()

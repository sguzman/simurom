import tomllib

def main():
    with open("assets/mini_game/characters/blonde.toml", "rb") as f:
        data = tomllib.load(f)
    character = data.get("character", {})
    segments = character.get("segments", [])
    print("Number of segments parsed in TOML:", len(segments))
    for i, seg in enumerate(segments):
        print(f"Segment {i}: id={seg.get('id')}, sprite={seg.get('sprite')}, layer_offset={seg.get('layer_offset')}")
        if "blink" in seg:
            print("  Blink config found!")
            print("  Blink frames count:", len(seg["blink"].get("blink_frames", [])))

if __name__ == "__main__":
    main()

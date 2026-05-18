use std::fs;
use simurom_schema::character::CharacterSpec;

fn main() {
    let content = fs::read_to_string("assets/mini_game/characters/blonde.toml").unwrap();
    let spec: CharacterSpec = toml::from_str(&content).unwrap();
    println!("Number of segments parsed: {}", spec.character.segments.len());
    for (i, seg) in spec.character.segments.iter().enumerate() {
        println!("Segment {}: id={}, sprite={}, layer_offset={}", i, seg.id, seg.sprite, seg.layer_offset);
        if let Some(ref blink) = seg.blink {
            println!("  Blink config found!");
            println!("  Blink frames count: {}", blink.blink_frames.as_ref().map(|f| f.len()).unwrap_or(0));
        }
    }
}

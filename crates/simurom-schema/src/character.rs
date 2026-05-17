#![forbid(unsafe_code)]

use serde::{
  Deserialize,
  Serialize
};

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct Vector2d {
  pub x: f32,
  pub y: f32
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct WindSwaySpec {
  pub amplitude:    f32,
  pub frequency:    f32,
  pub phase_offset: f32
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct BlinkSpec {
  pub blink_interval: f32,
  pub blink_duration: f32,
  pub closed_sprite:  String
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct SegmentSpec {
  pub id:           String,
  pub layer_offset: f32,
  pub sprite:       String,
  pub offset:       Vector2d,
  pub wind_sway: Option<WindSwaySpec>,
  pub blink:        Option<BlinkSpec>
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct ClothingSlotSpec {
  pub name:           String,
  pub default_sprite: Option<String>,
  pub layer_offset:   f32,
  pub offset:         Vector2d
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct CharacterConfig {
  pub name:           String,
  pub scale:          f32,
  pub segments:       Vec<SegmentSpec>,
  pub clothing_slots:
    Vec<ClothingSlotSpec>
}

#[derive(
  schemars::JsonSchema,
  Debug,
  Clone,
  Serialize,
  Deserialize,
)]
#[serde(deny_unknown_fields)]
pub struct CharacterSpec {
  pub character: CharacterConfig
}

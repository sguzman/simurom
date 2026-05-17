#![forbid(unsafe_code)]

use bevy::prelude::*;
use simurom_assets::resolve::bevy_load;
use simurom_schema::AssetRef;

use crate::{
  AssetsCacheRes,
  AssetsRootRes,
  ConfigRes,
  SimuromSprite
};

#[derive(Component, Debug, Clone)]
pub struct CharacterSegmentMarker;

#[derive(Component, Debug, Clone)]
pub struct WindSwaySegment {
  pub amplitude:    f32,
  pub frequency:    f32,
  pub phase_offset: f32
}

#[derive(
  Debug, Clone, Copy, PartialEq, Eq,
)]
pub enum AdvancedBlinkState {
  Open,
  Closing,
  Closed,
  Opening
}

#[derive(Component, Debug, Clone)]
pub struct BlinkingSegment {
  pub timer:          f32,
  pub blink_interval: f32,
  pub blink_duration: f32,
  pub open_handle:    Handle<Image>,
  pub closed_handle:  Handle<Image>,
  pub is_closed:      bool,

  // Advanced multi-frame fields
  pub is_advanced:      bool,
  pub base_interval:    f32,
  pub interval_delta:   f32,
  pub min_interval:     f32,
  pub max_interval:     f32,
  pub cooldown_seconds: f32,
  pub frame_duration:   f32,
  pub blink_frames: Vec<Handle<Image>>,
  pub state: AdvancedBlinkState,
  pub frame_index:      usize,
  pub frame_timer:      f32,
  pub lcg_seed:         u32
}

#[derive(Component, Debug, Clone)]
pub struct ClothingSlotSegment {
  pub slot_name: String
}

#[derive(
  Message, Event, Debug, Clone,
)]
pub struct SwapClothingEvent {
  pub entity:          Entity,
  pub slot_name:       String,
  pub new_sprite_path: String
}

pub struct CharacterSystemsPlugin;

impl Plugin for CharacterSystemsPlugin {
  fn build(
    &self,
    app: &mut App
  ) {
    app
      .add_message::<SwapClothingEvent>(
      )
      .add_systems(
        Update,
        (
          wind_sway_system,
          blinking_system,
          clothing_swap_system
        )
      );
  }
}

pub fn wind_sway_system(
  time: Res<Time>,
  mut query: Query<(
    &mut Transform,
    &WindSwaySegment
  )>
) {
  let t = time.elapsed_secs();
  for (mut tf, sway) in query.iter_mut()
  {
    let angle = sway.amplitude
      * (t
        * sway.frequency
        * 2.0
        * std::f32::consts::PI
        + sway.phase_offset)
        .sin();
    tf.rotation =
      Quat::from_rotation_z(angle);
  }
}

pub fn blinking_system(
  time: Res<Time>,
  mut query: Query<(
    &mut Sprite,
    &mut BlinkingSegment
  )>
) {
  let dt = time.delta_secs();
  for (mut sprite, mut blink) in
    query.iter_mut()
  {
    if blink.is_advanced {
      match blink.state {
        AdvancedBlinkState::Open => {
          blink.timer -= dt;
          if blink.timer <= 0.0 {
            // Transition to closing state, reset frame index to 0
            blink.state = AdvancedBlinkState::Closing;
            blink.frame_index = 0;
            blink.frame_timer = blink.frame_duration;
            // Apply frame 0 just in case
            if !blink.blink_frames.is_empty() {
              sprite.image = blink.blink_frames[0].clone();
            }
          }
        }
        AdvancedBlinkState::Closing => {
          blink.frame_timer -= dt;
          if blink.frame_timer <= 0.0 {
            blink.frame_timer = blink.frame_duration;
            if blink.frame_index + 1 < blink.blink_frames.len() {
              blink.frame_index += 1;
              sprite.image = blink.blink_frames[blink.frame_index].clone();
            } else {
              // Reached fully closed
              blink.state = AdvancedBlinkState::Closed;
              blink.timer = blink.cooldown_seconds;
            }
          }
        }
        AdvancedBlinkState::Closed => {
          blink.timer -= dt;
          if blink.timer <= 0.0 {
            // Transition to opening
            blink.state = AdvancedBlinkState::Opening;
            blink.frame_timer = blink.frame_duration;
          }
        }
        AdvancedBlinkState::Opening => {
          blink.frame_timer -= dt;
          if blink.frame_timer <= 0.0 {
            blink.frame_timer = blink.frame_duration;
            if blink.frame_index > 0 {
              blink.frame_index -= 1;
              sprite.image = blink.blink_frames[blink.frame_index].clone();
            } else {
              // Back to open (idle)
              blink.state = AdvancedBlinkState::Open;
              // Generate a deterministic random interval between min_interval and max_interval using LCG
              // seed = seed * 1103515245 + 12345
              blink.lcg_seed = blink.lcg_seed.wrapping_mul(1103515245).wrapping_add(12345);
              let pct = (blink.lcg_seed as f32) / (u32::MAX as f32);

              // Map to range [base_interval - interval_delta, base_interval + interval_delta]
              // while strictly clamping between [min_interval, max_interval]
              let mut next_interval = blink.base_interval - blink.interval_delta + pct * 2.0 * blink.interval_delta;
              if next_interval < blink.min_interval {
                next_interval = blink.min_interval;
              }
              if next_interval > blink.max_interval {
                next_interval = blink.max_interval;
              }
              blink.timer = next_interval;
            }
          }
        }
      }
    } else {
      blink.timer -= dt;
      if blink.timer <= 0.0 {
        if blink.is_closed {
          // Open the eyes
          blink.is_closed = false;
          sprite.image =
            blink.open_handle.clone();
          blink.timer =
            blink.blink_interval;
        } else {
          // Close the eyes
          blink.is_closed = true;
          sprite.image =
            blink.closed_handle.clone();
          blink.timer =
            blink.blink_duration;
        }
      }
    }
  }
}

pub fn clothing_swap_system(
  mut events: MessageReader<
    SwapClothingEvent
  >,
  mut query: Query<(
    &ChildOf,
    &mut Sprite,
    &mut SimuromSprite,
    &ClothingSlotSegment
  )>,
  assets: Res<AssetServer>,
  cfg: Res<ConfigRes>,
  assets_root: Res<AssetsRootRes>,
  mut asset_cache: ResMut<
    AssetsCacheRes
  >
) {
  for event in events.read() {
    for (
      parent,
      mut sprite,
      mut sim_sprite,
      slot
    ) in query.iter_mut()
    {
      if parent.parent() == event.entity
        && slot.slot_name
          == event.slot_name
      {
        let new_ref = AssetRef::String(
          event.new_sprite_path.clone()
        );
        let loaded =
          bevy_load::load_image_cached(
            &mut asset_cache.0,
            &assets,
            &cfg.0,
            &assets_root.0,
            &new_ref
          );
        match loaded {
          | Ok(handle) => {
            sprite.image = handle;
            sim_sprite.image = new_ref;
            tracing::info!(
              slot = %slot.slot_name,
              entity = ?event.entity,
              path = %event.new_sprite_path,
              "successfully swapped clothing slot"
            );
          }
          | Err(err) => {
            tracing::error!(
              slot = %slot.slot_name,
              entity = ?event.entity,
              error = %err,
              "failed to load new clothing sprite"
            );
          }
        }
      }
    }
  }
}

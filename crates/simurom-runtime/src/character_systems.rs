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

#[derive(Component, Debug, Clone)]
pub struct BlinkingSegment {
  pub timer:          f32,
  pub blink_interval: f32,
  pub blink_duration: f32,
  pub open_handle:    Handle<Image>,
  pub closed_handle:  Handle<Image>,
  pub is_closed:      bool
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

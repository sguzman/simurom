use bevy::prelude::*;
use tracing::instrument;

#[derive(
  Resource, Debug, Clone, Default,
)]
pub struct ActionMap {
  pub bindings:
    std::collections::HashMap<
      String,
      Vec<KeyCode>
    >
}

#[derive(
  Resource, Debug, Clone, Default,
)]
pub struct ActiveActions(
  pub std::collections::HashSet<String>
);

#[derive(Event, Debug, Clone)]
pub struct InputAction {
  pub name: String
}

#[instrument(level = "info", skip_all)]
pub fn input_system(
  keyboard: Res<ButtonInput<KeyCode>>,
  action_map: Res<ActionMap>,
  mut active_actions: ResMut<
    ActiveActions
  >,
  mut commands: Commands
) {
  for (name, keys) in
    action_map.bindings.iter()
  {
    let mut is_active = false;
    for key in keys {
      if keyboard.pressed(*key) {
        is_active = true;
      }
      if keyboard.just_pressed(*key) {
        tracing::info!(action = %name, "Input action triggered");
        commands.trigger(InputAction {
          name: name.clone()
        });
      }
    }

    if is_active {
      active_actions
        .0
        .insert(name.clone());
    } else {
      active_actions.0.remove(name);
    }
  }
}

#[derive(
  Component, Debug, Clone, Default,
)]
pub struct PopupText {
  pub timer: f32
}

#[instrument(level = "info", skip_all)]
pub fn input_action_observer(
  action: On<InputAction>,
  mut commands: Commands,
  player_query: Query<
    &Transform,
    With<crate::agents::PlayerAgent>
  >,
  interact_query: Query<(
    Entity,
    &Transform,
    &OnClick
  )>,
  existing_popups: Query<
    Entity,
    With<PopupText>
  >,
  entity_map: Res<crate::EntityMap>
) {
  let action_name = &action.name;
  if action_name
    .starts_with("transition:")
  {
    let path = action_name
      .strip_prefix("transition:")
      .unwrap();
    commands.write_message(
      crate::TransitionScene(
        std::path::PathBuf::from(path)
      )
    );
  } else if action_name == "interact" {
    if let Some(player_tf) =
      player_query.iter().next()
    {
      let player_pos = player_tf
        .translation
        .truncate();
      let mut nearest = None;
      let mut min_dist = 100.0; // Interaction radius

      for (_entity, tf, on_click) in
        interact_query.iter()
      {
        let dist = tf
          .translation
          .truncate()
          .distance(player_pos);
        if dist < min_dist {
          min_dist = dist;
          nearest =
            Some(on_click.0.clone());
        }
      }

      if let Some(target_action) =
        nearest
      {
        commands.trigger(InputAction {
          name: target_action
        });
      }
    }
  } else if action_name
    .starts_with("text:")
  {
    let message = action_name
      .strip_prefix("text:")
      .unwrap();
    tracing::info!(
      message,
      "Showing popup text"
    );
    // Despawn any existing popup text
    // entities so they never
    // overlap/stack!
    for entity in existing_popups.iter()
    {
      if let Ok(mut ent_cmds) =
        commands.get_entity(entity)
      {
        ent_cmds.despawn();
      }
    }
    // Simple implementation: spawn a UI
    // text or log it for now
    commands.spawn((
      Text2d::new(message),
      TextFont {
        font_size: 24.0,
        ..default()
      },
      TextColor(Color::WHITE),
      Transform::from_translation(
        Vec3::new(0.0, -250.0, 10.0)
      ),
      PopupText {
        timer: 3.5
      }
    ));
  } else if action_name
    .starts_with("swap_clothing:")
  {
    let suffix = action_name
      .strip_prefix("swap_clothing:")
      .unwrap();
    let parts: Vec<&str> =
      suffix.split(':').collect();
    if parts.len() == 3 {
      let target_id = parts[0];
      let slot_name =
        parts[1].to_string();
      let new_sprite_path =
        parts[2].to_string();

      if let Some(entities) =
        entity_map.0.get(target_id)
      {
        for &entity in entities {
          commands.trigger(crate::character_systems::SwapClothingEvent {
            entity,
            slot_name: slot_name.clone(),
            new_sprite_path: new_sprite_path.clone(),
          });
        }
      } else {
        tracing::error!(
          target_id,
          "No entities found in \
           entity_map for clothing \
           swap"
        );
      }
    } else {
      tracing::error!(
        suffix,
        "Invalid swap_clothing suffix \
         format; expected \
         target_id:slot_name:\
         sprite_path"
      );
    }
  }
}

pub fn popup_text_system(
  mut commands: Commands,
  time: Res<Time>,
  mut query: Query<(
    Entity,
    &mut PopupText
  )>
) {
  for (entity, mut popup) in
    query.iter_mut()
  {
    popup.timer -= time.delta_secs();
    if popup.timer <= 0.0 {
      if let Ok(mut ent_cmds) =
        commands.get_entity(entity)
      {
        ent_cmds.despawn();
      }
    }
  }
}

#[derive(
  Component, Debug, Clone, Default,
)]
pub struct Selectable;

#[derive(
  Component, Debug, Clone, Default,
)]
pub struct Draggable;

#[derive(Component, Debug, Clone)]
pub struct OnClick(pub String);

#[instrument(level = "info", skip_all)]
pub fn picking_system(
  mouse: Res<ButtonInput<MouseButton>>,
  windows: Query<&Window>,
  camera: Query<(
    &Camera,
    &GlobalTransform
  )>,
  query: Query<(
    Entity,
    &GlobalTransform,
    &OnClick,
    Option<&Selectable>
  )>,
  mut commands: Commands
) {
  if !mouse
    .just_pressed(MouseButton::Left)
  {
    return;
  }

  let window = windows
    .iter()
    .next()
    .expect("No window found");
  let Some((camera, camera_transform)) =
    camera.iter().next()
  else {
    return;
  };

  if let Some(cursor_pos) =
    window.cursor_position()
  {
    if let Ok(ray) = camera
      .viewport_to_world(
        camera_transform,
        cursor_pos
      )
    {
      let world_pos: Vec2 =
        ray.origin.truncate();
      for (
        entity,
        transform,
        on_click,
        _selectable
      ) in query.iter()
      {
        let pos = transform
          .translation()
          .truncate();
        // Simple radius-based picking
        if world_pos.distance(pos)
          < 50.0
        {
          tracing::info!(?entity, action = %on_click.0, "Entity clicked");
          commands.trigger(
            InputAction {
              name: on_click.0.clone()
            }
          );
        }
      }
    }
  }
}

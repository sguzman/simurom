use bevy::prelude::*;
use tracing::instrument;

#[derive(Component, Debug, Clone)]
pub struct Agent {
  pub kind:  String,
  pub state: String
}

#[derive(
  Component, Debug, Clone, Default,
)]
pub struct PlayerAgent {
  pub speed: f32
}

#[derive(Component, Debug, Clone)]
pub struct ScriptHook {
  pub on_tick: Option<String>
}

#[instrument(level = "info", skip_all)]
pub fn agent_tick_system(
  mut query: Query<(
    Entity,
    &mut Agent,
    &mut Transform,
    Option<&PlayerAgent>
  )>,
  _time: Res<Time>
) {
  for (
    entity,
    mut agent,
    mut transform,
    _player
  ) in query.iter_mut()
  {
    // Simple FSM stub
    match agent.kind.as_str() {
      | "wanderer" => {
        if agent.state == "idle" {
          agent.state =
            "moving".to_string();
          tracing::info!(
            ?entity,
            "Agent started wandering"
          );
        }
        // Basic wandering: move right
        transform.translation.x += 1.0;
      }
      | _ => {}
    }
  }
}

#[instrument(level = "info", skip_all)]
pub fn player_movement_system(
  active_actions: Res<
    crate::interaction::ActiveActions
  >,
  mut query: Query<(
    &mut Transform,
    &PlayerAgent
  )>,
  time: Res<Time>
) {
  for (mut transform, player) in
    query.iter_mut()
  {
    let mut move_dir = Vec2::ZERO;
    if active_actions
      .0
      .contains("move_up")
    {
      move_dir.y += 1.0;
    }
    if active_actions
      .0
      .contains("move_down")
    {
      move_dir.y -= 1.0;
    }
    if active_actions
      .0
      .contains("move_left")
    {
      move_dir.x -= 1.0;
    }
    if active_actions
      .0
      .contains("move_right")
    {
      move_dir.x += 1.0;
    }

    if move_dir != Vec2::ZERO {
      let speed = if player.speed > 0.0
      {
        player.speed
      } else {
        200.0
      };
      transform.translation += move_dir
        .normalize()
        .extend(0.0)
        * speed
        * time.delta_secs();
    }
  }
}

#[instrument(level = "info", skip_all)]
pub fn scripting_system(
  query: Query<(Entity, &ScriptHook)>
) {
  for (entity, hook) in query.iter() {
    if let Some(hook_name) =
      &hook.on_tick
    {
      tracing::info!(?entity, hook = %hook_name, "Executing script hook");
    }
  }
}

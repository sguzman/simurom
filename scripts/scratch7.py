import sys

with open('crates/simurom-runtime/src/lib.rs', 'r') as f:
    content = f.read()

content = content.replace("mut events: EventReader<ApplyPatch>", "mut events: bevy::ecs::event::EventReader<ApplyPatch>")
content = content.replace("scene.entities.push(entity.clone());", "scene.scene.entities.push(entity.clone());")
content = content.replace("scene.entities.retain(|e| e.id != *entity_id);", "scene.scene.entities.retain(|e| e.id != *entity_id);")
content = content.replace("scene.entities.iter_mut()", "scene.scene.entities.iter_mut()")

with open('crates/simurom-runtime/src/lib.rs', 'w') as f:
    f.write(content)

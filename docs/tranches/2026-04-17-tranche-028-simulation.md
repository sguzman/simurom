# Tranche 028 — Simulation

## Roadmap Items

### Simulation
- [x] Add `PhysicsSpec` to entity schema (body_type, mass, friction, restitution)
- [x] Add `ColliderSpec` to entity schema (box, circle)
- [x] Add `SimRegionSpec` to scene schema (gravity, bounds)
- [x] Add `ParticleSystemSpec` stub to schema
- [x] Implement simple `gravity_system` observer in runtime
- [x] Add `PhysicsBody` and `EntityHealth` components to runtime
- [x] Integrate `gravity_system` into `SimuromPlugin`
- [x] Update simulation-roadmap.md

## Verification Results

- `cargo check -p simurom-schema` passes.
- `cargo check -p simurom-runtime` passes.
- `SimTick` triggers `gravity_system` which applies constant gravity to `PhysicsBody`.
- `EntitySpec` now supports `physics`, `collider`, and `particles` tables.

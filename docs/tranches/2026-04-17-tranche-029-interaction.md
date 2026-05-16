# Tranche 029 — Interaction

## Roadmap Items
- [x] Implement `ActionMap` schema in TOML.
- [x] Implement input mapping system in `simurom-runtime`.
- [x] Add built-in actions: quit, reset, pause, step.
- [x] Implement picking (mouse hit test) for entities.
- [x] Update `interaction-roadmap.md`.

## Changes
- Added `InteractionSpec` and `ActionBinding` to `simurom-schema`.
- Added `EntityInteractionSpec` to `EntitySpec`.
- Implemented `interaction.rs` in `simurom-runtime`.
- Registered interaction systems in `lib.rs`.

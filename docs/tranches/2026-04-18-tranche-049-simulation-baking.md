# Tranche 049 — Simulation Baking

## Roadmap Items
### `export-roadmap.md`
- [x] Add simulation baking (bake command, trajectory export, playback interpolation)

### `tooling-roadmap.md`
- [x] Add bake subcommand for simulation trajectory export

## Changes
- **`simurom-schema`**: Added `baked` field to `Scene` struct.
- **`simurom-runtime`**: Created `bake` module with recorder and replay systems. Integrated with `SimuromRuntimePlugin`. Implemented headless `run_bake` runner.
- **`simurom-cli`**: Added `bake` subcommand and integrated runtime baking logic.

## Verification
- `cargo check -p simurom-runtime` — PASSED
- `cargo check -p simurom-cli` — PASSED
- Manual verification of subcommand registration and parameter parsing.

# Allowed dependencies

This project is a Cargo workspace split into **engine crates** (reusable libraries) and **apps** (binaries).

## Rules

- Apps may depend on engine crates.
- Engine crates must not depend on apps.
- “Schema” crates must be Bevy-free (no `bevy` dependency) so the format can be used by tools/validators without pulling a renderer.

## Current dependency graph

### Engine crates

- `simurom-config` (no Bevy)
  - depends on: `serde`, `toml`, `tracing`, `thiserror`
- `simurom-schema` (no Bevy)
  - depends on: `serde`, `toml`, `tracing`, `thiserror`
- `simurom-runtime`
  - depends on: `simurom-config`, `simurom-schema`, `tracing`, `thiserror`

### Apps

- `simurom-viewer`
  - depends on: `simurom-config`, `simurom-schema`, `simurom-runtime`


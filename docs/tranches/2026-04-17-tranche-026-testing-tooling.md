# Tranche 026 — Testing + Tooling

## Roadmap Items

### Testing
- [x] Add golden patch fixtures (`tests/fixtures/patches/*.toml`)
- [x] Add `patches` fixture test to simurom-schema
- [x] Add benchmarks for scene load/instantiate time
- [x] Add benchmarks for hot reload apply time and patch apply time

### Tooling CLI
- [x] Create `apps/simurom-cli`
- [x] Implement `validate` subcommand
- [x] Implement `run` subcommand
- [x] Implement `fmt` subcommand
- [x] Implement `resolve` subcommand
- [x] Implement `migrate` subcommand (stub)
- [x] Implement `diff` subcommand (basic)
- [x] Implement `new` subcommand
- [x] Implement `demo` subcommand
- [x] Add tracing controls via CLI flags

## Verification Results

- `cargo test -p simurom-schema` passes with 10 tests.
- `cargo build -p simurom-cli` compiles successfully.
- `simurom validate tests/fixtures/scenes/demo.toml` returns OK.
- `simurom new temp_scene.toml` creates a valid template.
- `simurom resolve tests/fixtures/scenes/demo.toml` prints pretty TOML.

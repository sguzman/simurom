# Tranche 061 (2026-05-17) — Debug Mode CLI, Low-Latency Present Mode, & FPS Limiter

Source roadmaps: `docs/roadmaps/rendering-roadmap.md`, `docs/roadmaps/tooling-roadmap.md`, `docs/roadmaps/interaction-roadmap.md`

- [x] Tooling (M0): Add support for a `--debug` / `-d` CLI flag in the `simurom run` subcommand to enable both developer egui panels and Bevy's World Inspector.
- [x] Rendering (M2): Add present mode configuration (`fifo`, `fiforelaxed`, `immediate`, `mailbox`, `autovsync`, `autonovsync`) to `RenderConfig` and map to Bevy's `PresentMode`.
- [x] Rendering (M2): Implement an accurate monotonic FPS limiter (`fps_limiter_system`) running in Bevy's `Last` stage using thread sleeping.
- [x] Interaction (M0): Force sequential execution ordering between `input_system` and `player_movement_system` to eliminate 1-frame latency.

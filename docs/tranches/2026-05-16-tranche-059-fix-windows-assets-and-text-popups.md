# Tranche 059 (2026-05-16) — fix windows asset paths and overlap in text popups

Source roadmaps: `docs/roadmaps/assets-roadmap.md`, `docs/roadmaps/interaction-roadmap.md`

- [x] Assets (M0): Normalize backslashes `\` in relative asset paths to forward slashes `/` on Windows 11 to allow Bevy's `AssetServer` to locate and load assets successfully.
- [x] Interaction (M1): Clear previous popup text HUD messages before spawning new ones to prevent text stacking/overlapping when interacting with objects.

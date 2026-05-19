# Character Assembler Tools

A centralized suite of Python-based analysis, cropping, transparency-keying, and alignment tools for simulating and reconstructing Bevy character scene assets.

Managed with [uv](https://github.com/astral-sh/uv) for fast, isolated virtual environment and dependency tracking.

## Dependencies

Primary package requirements:
- `numpy`
- `pillow`

Managed via `pyproject.toml`.

## How to Run the Tools

Since all scripts run in an isolated environment, always use `uv run` from the project root. For example, to regenerate the blinking eyes GIF:

```bash
uv run --project tools/character-assembler tools/character-assembler/generate_eyes_blinking_gif.py
```

Other available scripts include:
- `find_eyes_bbox.py`: Analyzes frames to find eye bounding boxes.
- `key_brows_smart.py`: High-fidelity transparency/alpha keying for assets.
- `align_hair.py` / `find_perfect_hair_alignment.py`: Algorithms for resolving scaling and offset alignments.

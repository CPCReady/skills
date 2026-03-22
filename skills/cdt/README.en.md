# 🎞️ cdt – ia2cdt Tape Image Toolkit

Full Python implementation of the ia2cdt workflow to create and inspect Amstrad CPC cassette images (`.cdt`/`.tzx`). No binaries, no installation scripts—just run the script with Python 3 on any OS.

## Highlights
- **Subcommand CLI**: `new`, `save`, `cat`, `check` similar to iaDSK.
- **Advanced encoding**: Turbo/Pure/Standard blocks plus headerless, Spectrum, and two custom split modes.
- **Custom timing**: Baud rate 1000–6000, per-block pauses, and per-file end pauses.
- **Rich output**: Markdown tables for humans, structured JSON for automations.
- **Reader + writer**: Inspect existing tapes, validate integrity, and append new files on the fly.

## Quick Start

```bash
cd skills/cdt
python3 scripts/ia2cdt.py new game.cdt
python3 scripts/ia2cdt.py save game.cdt --file loader.bas --baud 6000
python3 scripts/ia2cdt.py cat game.cdt
python3 scripts/ia2cdt.py check game.cdt
```

Requirements:
- Python 3.6+
- Standard library only (`argparse`, `math`, `json`, `os`)

## Command Reference

| Command | Description |
|---------|-------------|
| `new <cdt>` | Create a new tape with header + initial pause |
| `save <cdt> --file <input>` | Append a file using configurable encoding |
| `cat <cdt> [--format json]` | List blocks (Markdown by default, JSON optional) |
| `check <cdt>` | Validate structure, CRCs, headers |

### `save` Options

| Flag | Description |
|------|-------------|
| `--name` | AMSDOS name (max 16 chars, defaults to filename) |
| `--type {bin,bas,ascii}` | Override auto-detected type |
| `--baud <1000-6000>` | Custom baud rate (default 2000) |
| `--load-addr <addr>` | Load address (hex or decimal) |
| `--start-addr <addr>` | Call/exec address |
| `--tzx-method {0,1,2}` | `0` Turbo, `1` Pure Data, `2` Standard Speed |
| `--data-method {0..4}` | See next table |
| `--pause-header` | Pause after header block (ms) |
| `--pause-data` | Pause after data block (ms) |
| `--pause-file` | Pause after full file (ms) |

### Data Methods

| Method | Name | Description |
|--------|------|-------------|
| `0` | Blocks | Standard CPC blocks with AMSDOS headers |
| `1` | Headerless | Raw payload in CPC format (RAM inject, no header) |
| `2` | Spectrum | ZX/Spectrum standard-speed block (flag+checksum) |
| `3` | Two-blocks 2K | First block 2048B, remaining bytes second block |
| `4` | Two-blocks 1B | First block 1 byte, remaining bytes second block |

### Output Modes

- **Markdown (default)** – table showing block number, type, size, and decoded detail (header info, payload size, pauses).
- **JSON (`--format json`)** – machine-friendly metadata per block (`header`, `payload_bytes`, `pause_ms`). Ideal for CI scripts or linting existing tapes.

## Usage Scenarios

### Multi-file Tape with Custom Speeds

```bash
python3 scripts/ia2cdt.py new space.cdt
python3 scripts/ia2cdt.py save space.cdt --file fastloader.bas --baud 6000
python3 scripts/ia2cdt.py save space.cdt --file main.bin --name MAIN --load-addr 0x4000 --start-addr 0x4000 --baud 2000
python3 scripts/ia2cdt.py save space.cdt --file assets.bin --data-method 3 --baud 3000
python3 scripts/ia2cdt.py cat space.cdt
```

### Headerless Screen Load

```bash
python3 scripts/ia2cdt.py save demo.cdt \
  --file title.scr \
  --data-method 1 \
  --load-addr 0xC000 \
  --baud 4000 \
  --pause-file 8000
```

### ZX Spectrum Compatibility

```bash
python3 scripts/ia2cdt.py save zxport.cdt \
  --file port.tap \
  --data-method 2 \
  --tzx-method 2 \
  --pause-file 5000
```

### Automated Inspection

```bash
python3 scripts/ia2cdt.py cat game.cdt --format json | jq '.blocks[] | select(.header.filename=="MAIN")'
python3 scripts/ia2cdt.py check assets.cdt
```

## Tips & Troubleshooting

- **“Could not read file”** – ensure the CDT exists; run `new` first when building from scratch.
- **Tape fails in emulator** – lower baud rate (e.g., 2000 or 1000) and confirm start/load addresses with `cat --format json`.
- **Need reliable loaders** – combine `data-method 3` (2K + rest) with custom pauses for compatibility with picky firmware.
- **Spectrum mode** – automatically enforces Standard Speed pulses, ignoring turbo settings.

## Further Reading

- `references/cli-recipes.md` – exhaustive command cookbook.
- CPC Wiki (CDT/TZX format): <https://www.cpcwiki.eu/index.php/Format:CDT_tape_image_file_format>
- Amstrad Firmware Guide (timings): <https://archive.org/details/SOFT968TheAmstrad6128FirmwareManual>

---

The `cdt` skill mirrors the `dsk` skill structure to ease automation. Drop it into any `skills.sh` / Copilot workspace and run `python3 scripts/ia2cdt.py` directly—no installers, no compiled binaries.

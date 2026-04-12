# ROM (nocart) - Amstrad GX-4000 Cartridge Manager

This skill provides the Python port of the `nocart` tool, an interactive and automated tool designed to handle `.cpr` file cartridges. It transforms Amstrad `.dsk` floppy disk files into ready-to-use ROM images for the retro console.

## Main Commands

```bash
python3 scripts/nocart.py create disk.dsk game.cpr --command 'run"disc"'
python3 scripts/nocart.py check game.cpr
python3 scripts/nocart.py dumpdsk disk.dsk dump.bin
```

## Features

- **No external dependencies**: Runs entirely natively on Python 3 out of the box.
- **Interactive Prompts**: If you omit inputs such as source or destination in an interactive shell, you will be automatically prompted.
- **AI Ready Architecture (JSON output)**: The tool replaces normal execution logs with valid, parse-able JSON entries making it perfectly suitable for intelligent agents.
- **Universal compatibility**: It interacts with MV-CPC and Extended MFM DSK formats.

## Requirements

- **Python 3.6+**: Standard library only. No `pip install` required.

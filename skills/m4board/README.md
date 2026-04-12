# M4Board - Contol Remoto Amstrad CPC

This skill provides utilities for managing and pushing files to the Amstrad M4Board (WIFI interface).

## Documentation Languages

Please select your preferred language:

- 🇬🇧 [English Documentation](README.en.md)
- 🇪🇸 [Documentación en Español](README.es.md)

---

## Quick Start

You must run the wrapper script for your OS rather than the raw python file. This sets up dependencies.

```bash
# Set your M4Board IP first (optional step)
export M4BOARD_IP="192.168.1.100"

# Linux / Mac
./skills/m4board/scripts/run_m4board.sh <action> <args>

# Windows
.\skills\m4board\scripts\run_m4board.ps1 <action> <args>
```

For completely interactive prompt logic:
```bash
./skills/m4board/scripts/run_m4board.sh
```

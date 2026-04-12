# ROM (nocart) - Amstrad CPC Skill

This skill provides utilities for managing Amstrad GX-4000 ROM cartridge images (`.cpr`). It is powered by `nocart`, a tool that allows creating, dumping, and checking CPR files.

## Documentation Languages

Please select your preferred language:

- 🇬🇧 [English Documentation](README.en.md)
- 🇪🇸 [Documentación en Español](README.es.md)

---

## Quick Start

You can run the script directly with Python 3:

```bash
python3 scripts/nocart.py <action> [input_file] [output_file]
```

### Available Actions

- **create**: Create a .cpr file from a .dsk file, capable of being loaded on a GX-4000
- **dumpdsk**: Dump all the contents of a .dsk file as if it were written on a .cpr
- **check**: Check an existing .cpr file for correct RIFF and AMS! headers and chunks.

If you don't provide the necessary arguments and run it in an interactive terminal, it will prompt you for them.

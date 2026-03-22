# CDT Skill - Amstrad CPC Tape Image Management

Choose your language / Elige tu idioma:

- 🇬🇧 [English documentation](./README.en.md)
- 🇪🇸 [Documentación en español](./README.es.md)

---

## Quick Start

Create and manage Amstrad CPC tape images (.cdt) with Python:

```bash
# Create new tape
python3 scripts/ia2cdt.py new game.cdt

# Add files
python3 scripts/ia2cdt.py save game.cdt --file loader.bas
python3 scripts/ia2cdt.py save game.cdt --file main.bin --name "MAIN"

# List contents
python3 scripts/ia2cdt.py cat game.cdt
```

**Requirements**: Python 3.6+ (no additional dependencies)

For detailed documentation, select your language above.

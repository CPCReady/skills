# ia2cdt CLI Recipes

Complete reference for all ia2cdt.py commands and options.

## Output Format

**BREAKING CHANGE:** A partir de ahora, ia2cdt.py devuelve **JSON por defecto**.

- **Default:** JSON estructurado (optimizado para parseo automático por agentes IA)
- **Human-readable:** Añadir `--format markdown` para salida Markdown legible directamente

### Ejemplos de formato

```bash
# JSON (default) - Ideal para agentes IA
python3 ia2cdt.py cat game.cdt

# Markdown - Para lectura humana directa
python3 ia2cdt.py cat game.cdt --format markdown
```

**Para agentes IA:** Ejecutar comandos sin flags de formato, recibir JSON, parsear y presentar como Markdown al usuario.

## Command Structure

```
ia2cdt.py <command> [arguments] [options]
```

All commands support:
- `--format markdown` : Output in Markdown format (default: JSON)
- `--help` : Show command-specific help

---

## Command: new

Create a new empty CDT file with initial pause block.

**Syntax:**
```bash
ia2cdt.py new <cdt_file>
```

**Arguments:**
- `<cdt_file>` : Path to CDT file to create

**Example:**
```bash
ia2cdt.py new game.cdt
```

**Notes:**
- Creates minimal valid CDT with header + pause block (3000ms)
- Overwrites existing file without warning
- File is ready for `save` operations

---

## Command: save

Add a file to an existing CDT with full control over encoding parameters.

**Syntax:**
```bash
ia2cdt.py save <cdt_file> --file <input_file> [options]
```

**Required Arguments:**
- `<cdt_file>` : Existing CDT file to modify
- `--file <path>` : File to add to the tape

**Options:**

### File Identification
- `--name <name>` : Name displayed during load (max 16 chars, default: filename)
- `--type <type>` : File type: `bin`, `bas`, `ascii` (default: auto-detect from extension)

### Addresses
- `--load-addr <addr>` : Load address in memory (hex or decimal, default: 0x4000)
- `--start-addr <addr>` : Execution/call address (hex or decimal, default: 0x4000)

### Encoding Parameters
- `--baud <rate>` : Baud rate 1000-6000 (default: 2000)
  - Common: 1000 (slow, reliable), 2000 (standard), 6000 (fast loaders)
  
- `--tzx-method <n>` : TZX block method (default: 0)
  - `0` : Turbo Speed (0x11) - CPC standard with variable timing
  - `1` : Pure Data (0x14) - Data only, no pilot/sync
  - `2` : Standard Speed (0x10) - Fixed 1000 baud timing

- `--data-method <n>` : Data encoding method (default: 0)
  - `0` : Blocks - Standard CPC format with AMSDOS headers
  - `1` : Headerless - No AMSDOS header, direct RAM load
  - `2` : Spectrum - ZX Spectrum TAP format compatibility
  - `3` : Two blocks (2K+rest) - First block 2048 bytes, rest separate
  - `4` : Two blocks (1B+rest) - First block 1 byte, rest separate

### Timing/Pauses
- `--pause-header <ms>` : Pause after header block (default: 15)
- `--pause-data <ms>` : Pause after data block (default: 2560)
- `--pause-file <ms>` : Pause after complete file (default: 12000)

**Examples:**

Basic usage (auto-detect everything):
```bash
ia2cdt.py save game.cdt --file loader.bas
```

Specify name and addresses:
```bash
ia2cdt.py save game.cdt --file main.bin --name "MAIN" --load-addr 0x4000 --start-addr 0x4000
```

Fast loader (6000 bauds):
```bash
ia2cdt.py save game.cdt --file turbo.bin --baud 6000
```

Headerless screen load:
```bash
ia2cdt.py save demo.cdt --file screen.scr --data-method 1 --load-addr 0xC000 --baud 3000
```

Spectrum compatibility:
```bash
ia2cdt.py save zx.cdt --file game.tap --data-method 2 --tzx-method 2
```

Two-blocks loader:
```bash
ia2cdt.py save custom.cdt --file bigfile.bin --data-method 3 --baud 4000
```

Custom pauses:
```bash
ia2cdt.py save game.cdt --file menu.bin --pause-file 5000 --pause-data 1000
```

---

## Interactive Mode with Prompts

ia2cdt.py automatically detects binary files and prompts for missing parameters in interactive mode:

### Adding Binary File with Prompts

```bash
python3 ia2cdt.py save game.cdt --file loader.bin
```

**Interaction:**
```
[ia2cdt] Detectado archivo binario sin direcciones AMSDOS.

### Añadir archivo binario

Archivo: `loader.bin`

Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS.

Dirección de carga (--load-addr) en hexadecimal: 0x8000

Dirección de ejecución (--start-addr) en hexadecimal.
OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos.

Dirección de ejecución (--start-addr): 0x8000
```

**Note:** If the user doesn't enter a load address, the prompt will repeat until a valid value is provided.

### Adding Data File (Non-Executable)

```bash
python3 ia2cdt.py save game.cdt --file sprites.bin
```

**Interaction:**
```
Dirección de carga (--load-addr) en hexadecimal: 0xA000

Dirección de ejecución (--start-addr) en hexadecimal.
OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos.

Dirección de ejecución (--start-addr): 
¿Es este un archivo de datos (no ejecutable)? (s/n): s
```

(Uses load address 0xA000 as execution address)

### Non-Interactive Mode - ERROR if --load-addr Missing

```bash
echo "test" | python3 ia2cdt.py save game.cdt --file program.bin
# ERROR: Archivos binarios requieren --load-addr <dirección>.
# Ejemplo: --load-addr 0x4000
```

### Avoid Prompts (Automated Mode)

Provide all parameters explicitly to skip interactive prompts:

```bash
python3 ia2cdt.py save game.cdt --file program.bin \
  --load-addr 0x8000 --start-addr 0x8000 --type bin --baud 2000
```

---

## Command: cat

List all blocks in a CDT file with detailed information.

**Syntax:**
```bash
ia2cdt.py cat <cdt_file> [--format json]
```

**Arguments:**
- `<cdt_file>` : CDT file to inspect

**Options:**
- `--format json` : Output as JSON array (default: Markdown table)

**Example:**
```bash
ia2cdt.py cat game.cdt
```

**Output (Markdown):**
```
CDT: game.cdt
Version: 1.13

| Block # | Type           | Size   | Details                          |
|---------|----------------|--------|----------------------------------|
| 1       | Pause          | 3000ms | Initial pause                    |
| 2       | Turbo Speed    | 263B   | Header: LOADER (BAS)             |
| 3       | Turbo Speed    | 2816B  | Data: 2048 bytes                 |
| 4       | Pause          | 12000ms| File end pause                   |
| 5       | Turbo Speed    | 263B   | Header: MAIN (BIN) @ 0x4000      |
| 6       | Turbo Speed    | 8448B  | Data: 6144 bytes                 |
| 7       | Pause          | 12000ms| File end pause                   |
```

**Output (JSON):**
```json
{
  "cdt_file": "game.cdt",
  "version": "1.13",
  "blocks": [
    {
      "index": 1,
      "type": "Pause",
      "id": "0x20",
      "pause_ms": 3000
    },
    {
      "index": 2,
      "type": "Turbo Speed",
      "id": "0x11",
      "data_bytes": 263,
      "header": {
        "filename": "LOADER",
        "type": "BAS",
        "block_id": 1,
        "first_block": true,
        "last_block": true,
        "load_addr": "0x170",
        "start_addr": "0x0",
        "length": 512
      }
    },
    ...
  ]
}
```

---

## Command: check

Verify CDT file format integrity.

**Syntax:**
```bash
ia2cdt.py check <cdt_file>
```

**Arguments:**
- `<cdt_file>` : CDT file to validate

**Checks performed:**
- CDT header validity ("ZXTape!" signature)
- Block structure consistency
- CRC checksums (when applicable)
- Required fields presence

**Exit codes:**
- `0` : File is valid
- `1` : Format errors detected

**Example:**
```bash
ia2cdt.py check game.cdt
echo $?  # Check exit code
```

**Output:**
```
[OK] game.cdt: Valid CDT format
- Header: ZXTape! v1.13
- Blocks: 7 (all valid)
- No errors detected
```

Or if errors:
```
[ERROR] game.cdt: Invalid CDT format
- Block 3: CRC mismatch (expected 0xA3F2, got 0xA3F1)
- Block 5: Invalid header size
```

---

## Type Auto-Detection

When `--type` is omitted, file type is detected by extension:

| Extension         | Detected Type | AMSDOS Type |
|-------------------|---------------|-------------|
| `.bas`, `.BAS`    | `bas`         | 0x00        |
| `.bin`, `.BIN`    | `bin`         | 0x02        |
| `.txt`, `.asc`    | `ascii`       | 0x16        |
| Others            | `bin`         | 0x02        |

Override with `--type` if needed:
```bash
ia2cdt.py save game.cdt --file data.dat --type ascii
```

---

## Address Formats

Both hex and decimal accepted:

```bash
--load-addr 0x4000    # Hex
--load-addr 16384     # Decimal (same value)
--start-addr 0xC000   # Hex
--start-addr 49152    # Decimal (same value)
```

---

## Baud Rate Guidelines

| Baud | Use Case                    | Reliability |
|------|----------------------------|-------------|
| 1000 | Maximum compatibility      | ★★★★★       |
| 2000 | Standard CPC speed         | ★★★★☆       |
| 3000 | Faster loaders             | ★★★☆☆       |
| 4000 | Fast loaders (turbo)       | ★★☆☆☆       |
| 6000 | Maximum speed (risky)      | ★☆☆☆☆       |

**Recommendation**: Use 2000 for normal files, 1000 for long/critical data, 6000 only for small loaders.

---

## TZX Methods Comparison

| Method | ID   | Pilot | Sync | Use Case                           |
|--------|------|-------|------|------------------------------------|
| 0      | 0x11 | Yes   | Yes  | CPC standard (variable speed)      |
| 1      | 0x14 | No    | No   | Pure data (custom loaders)         |
| 2      | 0x10 | Yes   | Yes  | Fixed speed (spectrum compat)      |

---

## Data Methods Comparison

| Method | Name          | Description                           | Header | Blocks |
|--------|---------------|---------------------------------------|--------|--------|
| 0      | Blocks        | Standard CPC with AMSDOS headers      | Yes    | ≤8     |
| 1      | Headerless    | Direct RAM load, no header            | No     | 1      |
| 2      | Spectrum      | ZX Spectrum TAP format                | Custom | Varies |
| 3      | Two-blocks 2K | First 2048 bytes, then rest           | Yes    | 2      |
| 4      | Two-blocks 1B | First 1 byte, then rest               | Yes    | 2      |

---

## Complete Workflow Example

```bash
# 1. Create new tape
ia2cdt.py new mygame.cdt

# 2. Add fast BASIC loader (6000 bauds for speed)
ia2cdt.py save mygame.cdt --file loader.bas --name "LOADER" --baud 6000

# 3. Add main binary (standard 2000 bauds)
ia2cdt.py save mygame.cdt --file main.bin --name "MAIN" \
  --load-addr 0x4000 --start-addr 0x4000 --baud 2000

# 4. Add headerless screen (fast, direct to video RAM)
ia2cdt.py save mygame.cdt --file title.scr \
  --data-method 1 --load-addr 0xC000 --baud 3000

# 5. Add sprite data
ia2cdt.py save mygame.cdt --file sprites.bin --name "SPRITES" \
  --load-addr 0x8000 --baud 2000

# 6. Verify contents
ia2cdt.py cat mygame.cdt

# 7. Check integrity
ia2cdt.py check mygame.cdt

# 8. Export for debugging (JSON)
ia2cdt.py cat mygame.cdt --format json > mygame_info.json
```

---

## Scripting with JSON Output

```bash
# Get number of blocks
ia2cdt.py cat game.cdt --format json | jq '.blocks | length'

# Extract filenames
ia2cdt.py cat game.cdt --format json | jq '.blocks[].header.filename' | grep -v null

# Find blocks by type
ia2cdt.py cat game.cdt --format json | jq '.blocks[] | select(.type == "Turbo Speed")'

# Total data size
ia2cdt.py cat game.cdt --format json | jq '[.blocks[].data_bytes] | add'
```

---

## Error Handling

Common errors and solutions:

**"could not read file: <cdt>"**
- CDT doesn't exist → use `new` first

**"max input file size is 64K"**
- File > 65536 bytes → split file or use different format

**"unsupported block ID"**
- Corrupted CDT → use `check` to diagnose

**"invalid CDT format"**
- Not a CDT file or corrupted header

---

## Map File Support (Future)

Planned support for symbol map files:

```bash
ia2cdt.py save game.cdt --file code.bin \
  --map-file symbols.map --start-addr MAIN_ENTRY
```

Currently use explicit addresses only.

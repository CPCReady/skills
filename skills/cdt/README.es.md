# 🎞️ cdt – Toolkit de cintas ia2cdt

Implementación completa en Python del flujo ia2cdt para crear y analizar imágenes de cassette Amstrad CPC (`.cdt`/`.tzx`). No hay binarios ni instaladores: basta con Python 3 en cualquier sistema operativo.

## Destacados
- **CLI con subcomandos**: `new`, `save`, `cat`, `check` al estilo iaDSK.
- **Codificación avanzada**: bloques Turbo/Pure/Standard más modos headerless, Spectrum y divisiones personalizadas.
- **Timing configurable**: baudios 1000–6000, pausas individuales por bloque y por archivo.
- **Salida rica**: tablas Markdown para humanos y JSON estructurado para automatizaciones.
- **Lector y escritor**: inspecciona cintas existentes, valida integridad y agrega ficheros al vuelo.

## Inicio rápido

```bash
cd skills/cdt
python3 scripts/ia2cdt.py new juego.cdt
python3 scripts/ia2cdt.py save juego.cdt --file loader.bas --baud 6000
python3 scripts/ia2cdt.py cat juego.cdt
python3 scripts/ia2cdt.py check juego.cdt
```

Requisitos:
- Python 3.6+
- Solo librerías estándar (`argparse`, `math`, `json`, `os`)

## Referencia de comandos

| Comando | Descripción |
|---------|-------------|
| `new <cdt>` | Crea una cinta nueva con cabecera + pausa inicial |
| `save <cdt> --file <input>` | Añade un archivo con codificación configurable |
| `cat <cdt> [--format json]` | Lista bloques (Markdown por defecto, JSON opcional) |
| `check <cdt>` | Valida estructura, CRC y cabeceras |

### Opciones de `save`

| Flag | Descripción |
|------|-------------|
| `--name` | Nombre AMSDOS (máx. 16 chars, por defecto nombre del archivo) |
| `--type {bin,bas,ascii}` | Fuerza el tipo si no quieres auto-detector |
| `--baud <1000-6000>` | Velocidad personalizada (default 2000) |
| `--load-addr <addr>` | Dirección de carga (hex o decimal) |
| `--start-addr <addr>` | Dirección de llamada/ejecución |
| `--tzx-method {0,1,2}` | `0` Turbo, `1` Pure Data, `2` Standard Speed |
| `--data-method {0..4}` | Ver tabla siguiente |
| `--pause-header` | Pausa tras el bloque de cabecera (ms) |
| `--pause-data` | Pausa tras el bloque de datos (ms) |
| `--pause-file` | Pausa al terminar el fichero (ms) |

### Modos de datos

| Método | Nombre | Descripción |
|--------|--------|-------------|
| `0` | Blocks | Formato CPC clásico con cabeceras AMSDOS |
| `1` | Headerless | Sólo datos (ideal para pantallas/RAM directa) |
| `2` | Spectrum | Bloque estándar ZX con flag + checksum |
| `3` | Two-blocks 2K | Primer bloque 2048 bytes, resto en el segundo |
| `4` | Two-blocks 1B | Primer bloque 1 byte, resto en el segundo |

### Modos de salida

- **Markdown (default)** – tabla con número de bloque, tipo, tamaño y detalles decodificados (nombres AMSDOS, direcciones, tamaño real de payload).
- **JSON (`--format json`)** – metadatos por bloque (`header`, `payload_bytes`, `pause_ms`). Perfecto para pipelines CI o validadores.

## Escenarios de uso

### Cinta multiarchivo con velocidades mixtas

```bash
python3 scripts/ia2cdt.py new space.cdt
python3 scripts/ia2cdt.py save space.cdt --file fastloader.bas --baud 6000
python3 scripts/ia2cdt.py save space.cdt --file main.bin --name MAIN --load-addr 0x4000 --start-addr 0x4000 --baud 2000
python3 scripts/ia2cdt.py save space.cdt --file assets.bin --data-method 3 --baud 3000
python3 scripts/ia2cdt.py cat space.cdt
```

### Carga de pantalla sin cabecera

```bash
python3 scripts/ia2cdt.py save demo.cdt \
  --file titulo.scr \
  --data-method 1 \
  --load-addr 0xC000 \
  --baud 4000 \
  --pause-file 8000
```

### Compatibilidad ZX Spectrum

```bash
python3 scripts/ia2cdt.py save zxport.cdt \
  --file port.tap \
  --data-method 2 \
  --tzx-method 2 \
  --pause-file 5000
```

### Inspección automatizada

```bash
python3 scripts/ia2cdt.py cat juego.cdt --format json | jq '.blocks[] | select(.header.filename=="MAIN")'
python3 scripts/ia2cdt.py check datos.cdt
```

## Consejos y solución de problemas

- **“could not read file”** – asegúrate de que el CDT existe; ejecuta `new` antes de `save`.
- **La cinta no carga en emulador** – prueba con 2000 o 1000 baudios y confirma direcciones con `cat --format json`.
- **Necesitas loaders compatibles** – usa `data-method 3` (2K + resto) y ajusta las pausas para firmware exigente.
- **Modo Spectrum** – fuerza automáticamente Standard Speed, ignorando valores de `--tzx-method`.

## Recursos

- `references/cli-recipes.md` – guía completa de argumentos y recetas.
- Formato CDT/TZX en CPCWiki: <https://www.cpcwiki.eu/index.php/Format:CDT_tape_image_file_format>
- Firmware Guide (timings): <https://archive.org/details/SOFT968TheAmstrad6128FirmwareManual>

---

La skill `cdt` replica la estructura de `dsk` para integrarse sin fricción en `skills.sh`, Copilot o cualquier pipeline. Ejecuta `python3 scripts/ia2cdt.py` directamente y empieza a producir cintas CPC modernas en cuestión de segundos.

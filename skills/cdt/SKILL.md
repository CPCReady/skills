---
name: cdt
description: Crear y gestionar imágenes .cdt de cassette tape para Amstrad CPC desde automatizaciones. Usar cuando el usuario pida operar cintas CDT/TZX con ia2cdt (new, save, cat, check), cuando necesite control avanzado de velocidades de baudios (1000-6000), métodos TZX (turbo/pure data/standard), o codificación de datos (blocks/headerless/spectrum/two-blocks). Herramienta Python multiplataforma.
---

# cdt

## Flujo recomendado

1. Verificar que Python 3 esté disponible en el sistema.
2. Ejecutar directamente `ia2cdt.py` desde `scripts/` (no requiere instalación).
3. Usar salida Markdown por defecto para humanos; activar JSON con `--format json` para parseo automático.
4. **Para archivos binarios:** NUNCA asumir direcciones `--load-addr` o `--start-addr`. Dejar que ia2cdt.py las solicite interactivamente.

## Herramienta Python pura

Esta skill incluye una herramienta Python autocontenida en `scripts/ia2cdt.py`.

**No requiere instalación**: ejecuta directamente con Python 3:

```bash
python3 scripts/ia2cdt.py <command> [options]
```

Requisitos:
- Python 3.6+
- Solo usa bibliotecas estándar (sys, argparse, math)

## Comandos disponibles

Sintaxis tipo iaDSK con subcomandos:

```bash
ia2cdt.py new <cdt_file>
ia2cdt.py save <cdt_file> --file <input_file> [options]
ia2cdt.py cat <cdt_file> [--format json]
ia2cdt.py check <cdt_file>
```

### Comando: new

Crea un nuevo archivo CDT vacío (solo con bloque de pausa inicial).

```bash
ia2cdt.py new game.cdt
```

### Comando: save

Añade un archivo a un CDT existente con control completo de parámetros.

```bash
ia2cdt.py save game.cdt --file loader.bin --name "LOADER" --type bin --baud 2000
```

Opciones principales:
- `--file <path>`: Archivo a añadir (requerido)
- `--name <name>`: Nombre mostrado al cargar (max 16 chars)
- `--type <type>`: Tipo de archivo: `bin`, `bas`, `ascii` (auto-detecta por extensión)
- `--baud <rate>`: Velocidad 1000-6000 bauds (default: 2000)
- `--load-addr <addr>`: Dirección de carga (hex o decimal)
- `--start-addr <addr>`: Dirección de inicio/call (hex o decimal)
- `--tzx-method <n>`: Método TZX:
  - `0` = Turbo Speed (default, 0x11)
  - `1` = Pure Data (0x14)
  - `2` = Standard Speed (0x10)
- `--data-method <n>`: Codificación de datos:
  - `0` = Blocks (default, estándar CPC con headers)
  - `1` = Headerless (sin header, directo)
  - `2` = Spectrum (formato ZX Spectrum)
  - `3` = Two blocks (2K primer bloque + resto)
  - `4` = Two blocks (1 byte primer bloque + resto)
- `--pause-header <ms>`: Pausa tras header (default: 15)
- `--pause-data <ms>`: Pausa tras data (default: 2560)
- `--pause-file <ms>`: Pausa tras archivo completo (default: 12000)

### Comando: cat

Lista el contenido del CDT (todos los bloques).

```bash
ia2cdt.py cat game.cdt
ia2cdt.py cat game.cdt --format json
```

Salida Markdown (default):
- Tabla con columnas: Block #, Type, Size, Details
- Información de headers decodificados (nombre, tipo, dirección)

Salida JSON:
- Array de bloques con metadatos completos
- Útil para scripts automatizados

### Comando: check

Verifica la integridad del formato CDT (headers, checksums, estructura).

```bash
ia2cdt.py check game.cdt
```

Retorna exit code 0 si OK, 1 si hay errores.

## Formatos de entrada auto-detectados

El flag `--type` se puede omitir, la herramienta detecta por extensión:

- `.bas` → BASIC (`type=bas`)
- `.bin` → Binary (`type=bin`)
- `.txt`, `.asc` → ASCII (`type=ascii`)
- Otros → Binary por defecto

Override manual con `--type` si es necesario.

## Flujo de trabajo típico

### Crear tape multi-archivo

```bash
# 1. Crear CDT vacío
ia2cdt.py new game.cdt

# 2. Añadir loader BASIC rápido (6000 bauds)
ia2cdt.py save game.cdt --file loader.bas --baud 6000

# 3. Añadir código principal (2000 bauds estándar)
ia2cdt.py save game.cdt --file main.bin --name "MAIN" --load-addr 0x4000 --start-addr 0x4000

# 4. Añadir datos adicionales
ia2cdt.py save game.cdt --file sprites.bin --name "SPRITES" --load-addr 0x8000

# 5. Verificar contenido
ia2cdt.py cat game.cdt
```

### Usar métodos avanzados

```bash
# Headerless (sin AMSDOS header, carga directa en RAM)
ia2cdt.py save demo.cdt --file screen.scr --data-method 1 --load-addr 0xC000

# Formato Spectrum para compatibilidad
ia2cdt.py save zx.cdt --file game.tap --data-method 2

# Two-blocks para loaders especiales
ia2cdt.py save custom.cdt --file bigfile.bin --data-method 3
```

## Comparación con herramientas C

Esta herramienta Python **extiende** la funcionalidad de `ia2cdt` (C) y `cdt.py` original:

| Característica | ia2cdt (C) | cdt.py original | ia2cdt.py (esta skill) |
|----------------|------------|-----------------|------------------------|
| Leer CDT       | ❌         | ✅              | ✅                     |
| Escribir CDT   | ✅         | ✅              | ✅                     |
| Velocidades    | 1000-6000  | Solo 1000/2000  | 1000-6000              |
| TZX methods    | Turbo only | Turbo only      | Turbo + Pure + Standard|
| Data methods   | 4 tipos    | Solo blocks     | 5 tipos completos      |
| Pausas custom  | ❌         | Fijas           | Totalmente custom      |
| Salida formato | Silencioso | print()         | Markdown + JSON        |
| CLI moderna    | Flags      | Flags           | Subcomandos            |

## Prompts interactivos

`ia2cdt.py` incluye **validaciones automáticas** cuando se ejecuta en modo interactivo (terminal con stdin). Se presentan prompts para:

### 0. Nombre de imagen CDT - OBLIGATORIO

**Cuándo:** No se proporcionó el argumento posicional `<archivo.cdt>` en ningún comando.

**Prompt:**
```
### Nombre de imagen CDT

Nombre del archivo CDT:
```

- **OBLIGATORIO:** El usuario debe proporcionar un nombre de archivo CDT.
- El prompt se repite hasta que se ingrese un nombre válido.
- Si el nombre no termina en `.cdt`, se añade automáticamente la extensión.
- **En modo no interactivo (pipes/automatización):** El comando falla con error si falta el nombre.

**Ejemplo de error en modo no interactivo:**
```bash
echo "test" | python3 ia2cdt.py new
# ERROR: El comando 'new' requiere <archivo.cdt>
# Ejemplo: python3 ia2cdt.py new demo.cdt
```

### 1. Dirección de carga (load address) - OBLIGATORIO

**Cuándo:** Archivo binario detectado y no se proporcionó `--load-addr`.

**Prompt:**
```
### Añadir archivo binario

Archivo: `program.bin`

Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS.

Dirección de carga (--load-addr) en hexadecimal:
```

- **OBLIGATORIO:** El usuario debe proporcionar una dirección, no hay valor por defecto.
- El prompt se repite hasta que se ingrese una dirección válida.
- **En modo no interactivo (pipes/automatización):** El comando falla con error si falta `--load-addr`.

### 2. Dirección de ejecución (start address) - OBLIGATORIO

**Cuándo:** Archivo binario detectado y no se proporcionó `--start-addr`.

**Prompt:**
```
Dirección de ejecución (--start-addr) en hexadecimal.
OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos.

Dirección de ejecución (--start-addr):
```

- **OBLIGATORIO para ejecutables:** Si el archivo se ejecuta, debe tener dirección de ejecución.
- Puede dejarse vacío solo si es un archivo de datos (gráficos, música, etc.).
- Si se deja vacío, se pregunta si es archivo de datos; si confirma, usa la dirección de carga.
- **En modo no interactivo:** Si falta, usa la dirección de carga como fallback.

### Modo no interactivo

Cuando stdin no es un terminal (pipes, automatizaciones), ia2cdt.py **NO usa valores por defecto**:

- `--type`: auto-detectado si no se especifica
- `--load-addr`: **FALLA con error si es binario y no se proporciona**
- `--start-addr`: usa `--load-addr` como fallback (opcional)

**Ejemplo de error en modo no interactivo:**
```bash
echo "data" | python3 ia2cdt.py save demo.cdt --file program.bin
# ERROR: Archivos binarios requieren --load-addr <dirección>.
# Ejemplo: --load-addr 0x4000
```

### Evitar prompts (modo automatizado)

Para evitar prompts interactivos, proporciona **todos los parámetros explícitamente**:

```bash
python3 ia2cdt.py save demo.cdt --file program.bin \
  --load-addr 0x8000 --start-addr 0x8000 --type bin --baud 2000
```

## CRITICAL: Agent behavior for CDT commands

**NUNCA ASUMIR NOMBRES DE ARCHIVOS CDT NI DIRECCIONES DE MEMORIA**

Cuando el usuario solicita operar con un CDT, el agente **DEBE**:

1. **NO proporcionar** nombres de archivo CDT inventados (como `demo.cdt`, `tape.cdt`, etc.)
2. **NO proporcionar** `--load-addr` ni `--start-addr` para archivos binarios
3. **Dejar que ia2cdt.py solicite interactivamente** tanto el nombre del CDT como las direcciones al usuario
4. **Ejecutar el comando SIN estos parámetros** para activar los prompts interactivos

**INCORRECTO (NO HACER ESTO):**
```bash
python3 ia2cdt.py new demo.cdt
python3 ia2cdt.py save demo.cdt --file program.bin --load-addr 0x4000 --start-addr 0x4000
```

**CORRECTO:**
```bash
python3 ia2cdt.py new
python3 ia2cdt.py save --file program.bin
```

ia2cdt.py solicitará interactivamente:
- Nombre del archivo CDT (si no se proporciona el argumento posicional)
- Dirección de carga (--load-addr) - OBLIGATORIO para binarios
- Dirección de ejecución (--start-addr) - OBLIGATORIO para ejecutables

**Excepciones:** Solo proporcionar estos parámetros si:
- El usuario los especificó explícitamente en su solicitud
- Se está ejecutando en modo no interactivo (automatización)

## Referencias adicionales

- Detalle completo de opciones: `references/cli-recipes.md`
- Formato CDT/TZX: https://www.cpcwiki.eu/index.php/Format:CDT_tape_image_file_format
- Firmware guide (timings): https://archive.org/details/SOFT968TheAmstrad6128FirmwareManual

## Troubleshooting

**Error: "Python not found"**
- Instalar Python 3.6+ desde python.org o gestor de paquetes del sistema.

**Error: "could not read file"**
- Verificar que el CDT existe antes de usar `save`.
- Usar `new` para crear CDT nuevo primero.

**Archivo no carga en emulador**
- Probar con baud rate más bajo (2000 o 1000).
- Verificar direcciones de carga con `cat --format json`.
- Usar `check` para validar integridad.

**Output muy verboso**
- Por defecto usa Markdown legible.
- Para scripts usar `--format json` y parsear.

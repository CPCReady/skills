---
name: dsk
description: Crear, editar y gestionar imágenes .dsk de disco para Amstrad CPC desde automatizaciones. Usar cuando el usuario pida operar discos DSK (new, cat, free, get, put-bin, put-ascii, put-raw, era, list, check, dump). Herramienta Python pura multiplataforma (Windows, Linux, macOS). No requiere instalación de binarios.
---

# dsk

## Flujo recomendado

1. Verificar que Python 3 esté disponible en el sistema.
2. Ejecutar `iadsk.py` directamente:
   ```bash
   python3 scripts/iadsk.py demo.dsk --cat
   ```
3. Usar salida Markdown por defecto para humanos.
4. Comandos disponibles:
   - `new` - Crear DSK
   - `cat` - Listar archivos
   - `free` - Espacio libre
   - `put-bin` - Añadir binario con header AMSDOS
   - `put-ascii` - Añadir archivo ASCII
   - `put-raw` - Añadir archivo raw
   - `get` - Extraer archivo
   - `era` - Borrar archivo
   - `list` - Ver contenido de archivo
   - `check` - Verificar formato DSK
   - `dump` - Info detallada

## Requisitos

- Python 3.6+
- Solo usa bibliotecas estándar (stdlib only)
- Multiplataforma: Windows, macOS, Linux

## Ejecutar iadsk.py

macOS/Linux:

```bash
python3 scripts/iadsk.py demo.dsk --new
python3 scripts/iadsk.py demo.dsk --cat
python3 scripts/iadsk.py demo.dsk --free
```

Windows:

```powershell
python scripts/iadsk.py demo.dsk --new
python scripts/iadsk.py demo.dsk --cat
python scripts/iadsk.py demo.dsk --free
```

Usando wrappers (alternativa):

```bash
./scripts/run_iadsk.sh -- demo.dsk --cat
```

```powershell
.\scripts\run_iadsk.ps1 -- demo.dsk --cat
```

## Comandos disponibles

Usar esta guía rápida (ver detalle en `references/cli-recipes.md`):

```bash
# Crear y gestionar DSK
iadsk.py demo.dsk --new              # Crear DSK vacío
iadsk.py demo.dsk --cat             # Listar archivos
iadsk.py demo.dsk --free            # Ver espacio libre
iadsk.py demo.dsk --check           # Verificar formato
iadsk.py demo.dsk --dump            # Info detallada

# Añadir archivos
iadsk.py demo.dsk --put-bin programa.bas    # Binario con header AMSDOS
iadsk.py demo.dsk --put-ascii readme.txt   # Archivo ASCII
iadsk.py demo.dsk --put-raw datos.bin     # Archivo raw

# Gestionar archivos
iadsk.py demo.dsk --list programa.bas      # Ver contenido archivo
iadsk.py demo.dsk --list programa.bas --hex  # Ver como hex dump
iadsk.py demo.dsk --get 0 --output ./file.bin  # Extraer por índice
iadsk.py demo.dsk --era programa.bas        # Borrar archivo
```

## Formato de salida

Solo Markdown legible para humanos.

## Presenting results to the user

**IMPORTANT:** The iadsk.py output is already in Markdown format ready to render. The agent MUST:

- **Hide the command execution** from the user (don't show the bash tool call or raw output in a code block)
- **Present the result as rendered Markdown** by copying the script output directly into the response text, not as a code block
- Show the complete output as returned by iadsk.py, without summarizing, omitting rows, or reinterpreting
- Do NOT show markdown source code (like `| col | col |`); the user should see rendered tables, lists, and formatted headings
- If the output includes multiple sections (e.g., Catalog + Space), show them all complete
- Do NOT mention the executed command, binary path, or any technical invocation details
- The user should only see the final formatted result

**Example workflow:**
1. Execute internally: `python3 scripts/iadsk.py demo.dsk --cat`
2. Capture the markdown output
3. Present to user: Paste the markdown directly in your text response so it renders as formatted tables/headings, not as code

## Validación

Ejecutar en macOS/Linux:

```bash
python3 scripts/iadsk.py --version
```

Ejecutar en Windows:

```powershell
python scripts/iadsk.py --version
```

Validar que muestra "IADSK Tool Version 1.0.0"

## Recursos

- `scripts/iadsk.py`: herramienta principal (Python puro)
- `scripts/run_iadsk.sh` y `scripts/run_iadsk.ps1`: wrappers
- `scripts/install_iadsk.sh` y `scripts/install_iadsk.ps1`: placeholders
- `references/cli-recipes.md`: recetas de uso detalladas
- `tests/test_iadsk_commands.sh`: suite de tests exhaustiva

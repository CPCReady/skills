---
name: dsk
description: Instalar, actualizar y ejecutar iaDSK para trabajar con imágenes .dsk de Amstrad CPC desde automatizaciones. Usar cuando el usuario pida operar discos DSK con iaDSK (help, new, cat, free, save, get, era, list, basic, ascii, hex, disasm, dams), cuando necesite instalación multiplataforma (Windows, Linux o macOS), o cuando haya que garantizar que iaDSK quede instalado antes de ejecutar comandos.
---

# dsk

## Flujo recomendado

1. Verificar si `iaDSK` está disponible en `PATH`.
2. Instalar `iaDSK` con script nativo del sistema:
   - macOS/Linux: `scripts/install_iadsk.sh`
   - Windows: `scripts/install_iadsk.ps1`
3. Ejecutar comandos con wrapper nativo:
   - macOS/Linux: `scripts/run_iadsk.sh`
   - Windows: `scripts/run_iadsk.ps1`
4. La salida por defecto es JSON para facilitar parseo. Los agentes deben formatear esta salida como Markdown antes de presentarla al usuario.
5. **Para archivos binarios:** NUNCA asumir direcciones `--load` o `--exec`. Dejar que el wrapper las solicite interactivamente.

## Instalación sin compilación

Esta skill incluye binarios precompilados en `assets/bin/` para:

- `linux-x64`
- `linux-arm64`
- `macos-x64`
- `macos-arm64`
- `windows-x64`

Instalar:

```bash
./scripts/install_iadsk.sh
```

```powershell
.\scripts\install_iadsk.ps1
```

Opciones:

- `--install-dir <path>` en shell.
- `-InstallDir <path>` en PowerShell.
- `--json` / `-Json` para salida estructurada.

El instalador copia el binario correcto por SO/arquitectura a:

- Linux/macOS: `~/.local/bin/iaDSK`
- Windows: `%USERPROFILE%\\bin\\iaDSK.exe`

## Ejecutar iaDSK por sistema operativo

macOS/Linux:

```bash
./scripts/run_iadsk.sh -- help
./scripts/run_iadsk.sh -- free --dsk demo.dsk
./scripts/run_iadsk.sh --format markdown -- free --dsk demo.dsk
```

Windows:

```powershell
.\scripts\run_iadsk.ps1 -- help
.\scripts\run_iadsk.ps1 -- free --dsk demo.dsk
.\scripts\run_iadsk.ps1 -Format markdown -- free --dsk demo.dsk
```

Resolución de binario (prioridad):

1. Ruta explícita (`--binary` / `-Binary`)
2. `PATH`
3. ruta instalada por defecto
4. binario embebido en `assets/bin/<so-arquitectura>/`

Formato de salida:

- **Por defecto: JSON** para facilitar parseo automático por agentes IA.
- **Markdown para lectura directa:**
  - shell: `--format markdown`
  - PowerShell: `-Format markdown`
- **Compatibilidad:** alias `--raw-json` / `-RawJson` obsoletos (siempre devuelve JSON sin formato).

## Comandos base de iaDSK

Usar esta guía rápida (ver detalle en `references/cli-recipes.md`):

- `help [--command <cmd>]`
- `new --dsk <path>`
- `cat --dsk <path>`
- `free --dsk <path>`
- `save --dsk <path> --file <host_path> [opciones]`
- `get --dsk <path> --file <amsdos_name> [--output <host_path>]`
- `era --dsk <path> --file <amsdos_name>`
- `list/basic/ascii/hex/disasm/dams --dsk <path> --file <amsdos_name>`

Aliases válidos:

- `import` -> `save`
- `export` -> `get`
- `rm` -> `era`
- `disassemble` -> `disasm`

## Prompts interactivos

Los wrappers (`run_iadsk.sh` y `run_iadsk.ps1`) incluyen **validaciones automáticas** cuando el usuario ejecuta en modo interactivo (terminal con stdin). Se presentan prompts para:

### 0. Nombre de imagen DSK - OBLIGATORIO

**Cuándo:** No se proporcionó `--dsk <archivo.dsk>` en ningún comando (excepto `help`).

**Prompt:**
```
### Nombre de imagen DSK

Nombre del archivo DSK:
```

- **OBLIGATORIO:** El usuario debe proporcionar un nombre de archivo DSK.
- El prompt se repite hasta que se ingrese un nombre válido.
- Si el nombre no termina en `.dsk`, se añade automáticamente la extensión.
- **En modo no interactivo (pipes/automatización):** El comando falla con error si falta `--dsk`.

**Ejemplo de error en modo no interactivo:**
```bash
echo "test" | ./scripts/run_iadsk.sh -- new
# ERROR: El comando 'new' requiere --dsk <nombre.dsk>
# Ejemplo: --dsk demo.dsk
```

### 1. Verificación de sobrescritura

**Cuándo:** El archivo ya existe en el DSK y no se proporcionó `--force`.

**Prompt:**
```
⚠️  El archivo 'PROGRAM.BIN' ya existe en el disco.

¿Deseas sobrescribir? (s/n) [n]:
```

- Si el usuario confirma (s/y), se agrega automáticamente `--force`.
- Si el usuario cancela o presiona Enter, se aborta la operación.

### 2. Tipo de archivo AMSDOS

**Cuándo:** No se especificó `--type`.

**Prompt:**
```
Tipo de archivo AMSDOS:
  1) ascii   - Archivo de texto ASCII
  2) binary  - Archivo binario con cabecera AMSDOS
  3) raw     - Datos crudos sin cabecera

Selecciona tipo [2]:
```

- Por defecto: `2 (binary)` para archivos binarios, `1 (ascii)` para texto detectado.
- Los wrappers detectan automáticamente texto vs binario mediante inspección del contenido y extensión.

### 3. Dirección de carga (load address) - OBLIGATORIO

**Cuándo:** Archivo binario detectado y no se proporcionó `--load`.

**Prompt:**
```
### Añadir archivo binario

Archivo: `program.bin`

Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS.

Dirección de carga (--load) en hexadecimal:
```

- **OBLIGATORIO:** El usuario debe proporcionar una dirección, no hay valor por defecto.
- El prompt se repite hasta que se ingrese una dirección válida.
- **En modo no interactivo (pipes/automatización):** El comando falla con error si falta `--load`.

### 4. Dirección de ejecución (exec address) - OBLIGATORIO

**Cuándo:** Archivo binario detectado y no se proporcionó `--exec`.

**Prompt:**
```
Dirección de ejecución (--exec) en hexadecimal.
OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos.

Dirección de ejecución (--exec):
```

- **OBLIGATORIO para ejecutables:** Si el archivo se ejecuta, debe tener dirección de ejecución.
- Puede dejarse vacío solo si es un archivo de datos (gráficos, música, etc.).
- **En modo no interactivo:** No se solicita (el usuario debe proporcionar `--exec` si es necesario).

### Modo no interactivo

Cuando stdin no es un terminal (pipes, automatizaciones), los wrappers **NO usan valores por defecto**:

- `--type`: auto-detectado si no se especifica
- `--load`: **FALLA con error si es binario y no se proporciona**
- `--exec`: no se solicita (opcional)
- Sobrescritura: falla si el archivo existe (requiere `--force` explícito)

**Ejemplo de error en modo no interactivo:**
```bash
echo "data" | ./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin
# ERROR: Archivos binarios requieren --load <dirección>.
# Ejemplo: --load 0x4000
```

### Evitar prompts (modo automatizado)

Para evitar prompts interactivos, proporciona **todos los parámetros explícitamente**:

```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin \
  --type binary --load 0x8000 --exec 0x8000 --force
```

## CRITICAL: Agent behavior for DSK commands

**NUNCA ASUMIR NOMBRES DE ARCHIVOS DSK NI DIRECCIONES DE MEMORIA**

Cuando el usuario solicita operar con un DSK, el agente **DEBE**:

1. **NO proporcionar** nombres de archivo DSK inventados (como `demo.dsk`, `disk.dsk`, etc.)
2. **NO proporcionar** `--load` ni `--exec` para archivos binarios
3. **Dejar que el wrapper solicite interactivamente** tanto el nombre del DSK como las direcciones al usuario
4. **Ejecutar el comando SIN estos parámetros** para activar los prompts interactivos

**INCORRECTO (NO HACER ESTO):**
```bash
./scripts/run_iadsk.sh -- new --dsk demo.dsk
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin --load 0x4000 --exec 0x4000
```

**CORRECTO:**
```bash
./scripts/run_iadsk.sh -- new
./scripts/run_iadsk.sh -- save --file program.bin
```

El wrapper solicitará interactivamente:
- Nombre del archivo DSK (si no se proporciona `--dsk`)
- Tipo de archivo (ascii/binary/raw)
- Dirección de carga (--load) - OBLIGATORIO para binarios
- Dirección de ejecución (--exec) - OBLIGATORIO para ejecutables

**Excepciones:** Solo proporcionar estos parámetros si:
- El usuario los especificó explícitamente en su solicitud
- Se está ejecutando en modo no interactivo (automatización)

## Presenting results to the user

**IMPORTANT:** iaDSK returns JSON by default. The agent MUST:

1. **Execute the command** (no format flag needed - JSON is default)
2. **Parse the JSON response** to extract relevant data
3. **Format as Markdown table** with appropriate columns:
   - **Name**: Filename from `name` field
   - **User**: User number from `user` field (0-15)
   - **Size**: Size from `size_kb` field with "K" suffix
   - **Load**: Convert `load` (decimal) to hex with "0x" prefix (e.g., 16384 → 0x4000)
   - **Exec**: Convert `exec` (decimal) to hex with "0x" prefix (e.g., 16384 → 0x4000)
   - **Attr**: Combine attribute flags:
     - `read_only: true` → "R"
     - `system: true` → "S"
     - Both true → "RS"
     - Both false → "" (empty)
4. **Add summary line**: Show `used_kb` / `total_kb` (e.g., "2K / 178K used")
5. **Present formatted Markdown** to user (hide raw command and JSON)

**JSON structure for `cat` command:**
```json
{
  "dsk": "/path/to/file.dsk",
  "entries": [
    {
      "name": "PROGRAM.BIN",
      "user": 0,
      "load": 16384,           // DECIMAL - convert to 0x4000
      "exec": 16384,           // DECIMAL - convert to 0x4000
      "size_bytes": 2048,
      "size_kb": 2,
      "read_only": true,       // → Display "R"
      "system": false          // → Display "S"
    }
  ],
  "total_kb": 178,
  "used_kb": 2,
  "free_kb": 176
}
```

**Example formatted output to present:**
```markdown
| Name        | User | Size | Load   | Exec   | Attr |
|-------------|------|------|--------|--------|------|
| PROGRAM.BIN |    0 |   2K | 0x4000 | 0x4000 | R    |
| DATA.BIN    |    0 |   1K | 0x8000 | 0x8000 |      |

2K / 178K used
```

**DO NOT:**
- Show the raw bash command to the user
- Show raw JSON output in a code block
- Mention binary paths or technical execution details
- Summarize or omit entries - show all files

**User should only see:** The final formatted Markdown table with all entries and summary.

## Validación mínima tras instalación

Ejecutar en macOS/Linux:

```bash
./scripts/run_iadsk.sh -- help
```

Ejecutar en Windows:

```powershell
.\scripts\run_iadsk.ps1 -- help
```

Validar que:

- Sin flags extra, la salida es **JSON válido** de `iaDSK`.
- Con `--format markdown` / `-Format markdown`, la salida es Markdown legible.
- En modo JSON, `meta.program` es `iaDSK`.

## Recursos

- `assets/bin/*`: binarios precompilados por plataforma.
- `scripts/install_iadsk.sh` y `scripts/install_iadsk.ps1`: instalación sin compilación.
- `scripts/run_iadsk.sh` y `scripts/run_iadsk.ps1`: ejecución portable.
- `references/cli-recipes.md`: recetas de uso en modo friendly y JSON.

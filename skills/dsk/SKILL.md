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
4. Usar salida Markdown por defecto para humanos; activar JSON solo cuando se necesite parseo automático.
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
./scripts/run_iadsk.sh --format json -- free --dsk demo.dsk
```

Windows:

```powershell
.\scripts\run_iadsk.ps1 -- help
.\scripts\run_iadsk.ps1 -- free --dsk demo.dsk
.\scripts\run_iadsk.ps1 -Format json -- free --dsk demo.dsk
```

Resolución de binario (prioridad):

1. Ruta explícita (`--binary` / `-Binary`)
2. `PATH`
3. ruta instalada por defecto
4. binario embebido en `assets/bin/<so-arquitectura>/`

Formato de salida:

- Por defecto: Markdown legible para usuario.
- JSON para automatización:
  - shell: `--format json` (compat: `--raw-json`)
  - PowerShell: `-Format json` (compat: `-RawJson`)

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

## Prompts interactivos al añadir archivos

Los wrappers (`run_iadsk.sh` y `run_iadsk.ps1`) incluyen **validaciones automáticas** para el comando `save`. Cuando el usuario ejecuta en modo interactivo (terminal con stdin), se presentan prompts para:

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

## CRITICAL: Agent behavior for save command

**NUNCA ASUMIR VALORES PARA --load Y --exec**

Cuando el usuario solicita añadir un archivo binario a un DSK, el agente **DEBE**:

1. **NO proporcionar** `--load` ni `--exec` en el comando
2. **Dejar que el wrapper solicite interactivamente** estas direcciones al usuario
3. **Ejecutar el comando SIN estos parámetros** para activar los prompts interactivos

**INCORRECTO (NO HACER ESTO):**
```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin --type binary --load 0x4000 --exec 0x4000
```

**CORRECTO:**
```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin
```

El wrapper detectará automáticamente que es un archivo binario y solicitará:
- Tipo de archivo (ascii/binary/raw)
- Dirección de carga (--load) - OBLIGATORIO para binarios
- Dirección de ejecución (--exec) - OBLIGATORIO para ejecutables

**Excepciones:** Solo proporcionar `--load` y `--exec` si:
- El usuario los especificó explícitamente en su solicitud
- Se está ejecutando en modo no interactivo (automatización)

## Presenting results to the user

**IMPORTANT:** The iaDSK output is already in Markdown format ready to render. The agent MUST:

- **Hide the command execution** from the user (don't show the bash tool call or raw output in a code block)
- **Present the result as rendered Markdown** by copying the script output directly into the response text, not as a code block
- Show the complete output as returned by iaDSK, without summarizing, omitting rows, or reinterpreting
- Do NOT show markdown source code (like `| col | col |`); the user should see rendered tables, lists, and formatted headings
- If the output includes multiple sections (e.g., Catalog + Space), show them all complete
- Do NOT mention the executed command, binary path, or any technical invocation details
- The user should only see the final formatted result

**Example workflow:**
1. Execute internally: `./scripts/run_iadsk.sh -- cat --dsk demo.dsk`
2. Capture the markdown output
3. Present to user: Paste the markdown directly in your text response so it renders as formatted tables/headings, not as code

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

- Sin flags extra, la salida es Markdown legible para usuario.
- En modo JSON (`--format json` / `-Format json`), la salida es JSON válido de `iaDSK`.
- En modo JSON, `meta.program` es `iaDSK`.

## Recursos

- `assets/bin/*`: binarios precompilados por plataforma.
- `scripts/install_iadsk.sh` y `scripts/install_iadsk.ps1`: instalación sin compilación.
- `scripts/run_iadsk.sh` y `scripts/run_iadsk.ps1`: ejecución portable.
- `references/cli-recipes.md`: recetas de uso en modo friendly y JSON.

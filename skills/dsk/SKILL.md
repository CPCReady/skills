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

## Presentación de resultados al usuario

**IMPORTANTE:** La salida de iaDSK ya está en formato Markdown listo para renderizar. El agente DEBE:

- Mostrar la salida completa del comando tal como la devuelve iaDSK, sin resumir, sin omitir filas, sin reinterpretar.
- NO hacer un resumen ni una versión simplificada de la tabla o los datos.
- NO mostrar el código Markdown en crudo (como `| col | col |`); renderizarlo para que el usuario lo vea como tabla, lista y títulos formateados.
- Si la salida incluye varias secciones (ej. Catalogo + Espacio), mostrarlas todas completas.
- NO mostrar ni mencionar el comando ejecutado, la ruta del binario, ni ningún detalle técnico de invocación. El usuario solo debe ver el resultado final formateado.

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

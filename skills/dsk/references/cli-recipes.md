# Recetas CLI de iaDSK

## Patron general

1. Ejecutar wrappers de la skill (`run_iadsk.sh` o `run_iadsk.ps1`).
2. Por defecto, leer salida Markdown (titulo, tablas y bloques).
3. Si necesitas parseo, usar modo JSON:
   - shell: `--format json` (compat: `--raw-json`)
   - PowerShell: `-Format json` (compat: `-RawJson`)

## Instalación desde binarios embebidos

macOS/Linux:

```bash
./scripts/install_iadsk.sh
```

Windows:

```powershell
.\scripts\install_iadsk.ps1
```

No compila: copia el ejecutable adecuado desde `assets/bin/<plataforma>/`.

## Comandos frecuentes

```bash
iaDSK help
iaDSK new --dsk demo.dsk
iaDSK cat --dsk demo.dsk
iaDSK free --dsk demo.dsk
```

```bash
iaDSK save --dsk demo.dsk --file programa.bas --type ascii
iaDSK save --dsk demo.dsk --file loader.bin --type binary --load 8000 --exec 8000
iaDSK get --dsk demo.dsk --file programa.bas --output ./programa.bas
iaDSK era --dsk demo.dsk --file programa.bas
```

```bash
iaDSK list --dsk demo.dsk --file programa.bas
iaDSK basic --dsk demo.dsk --file programa.bas --split-lines
iaDSK ascii --dsk demo.dsk --file readme.txt
iaDSK hex --dsk demo.dsk --file loader.bin
iaDSK disasm --dsk demo.dsk --file loader.bin
iaDSK dams --dsk demo.dsk --file source.dam
```

## Ejecucion con wrappers (recomendado)

macOS/Linux:

```bash
./scripts/run_iadsk.sh -- new --dsk demo.dsk
./scripts/run_iadsk.sh -- cat --dsk demo.dsk
./scripts/run_iadsk.sh --format json -- cat --dsk demo.dsk
```

Windows:

```powershell
.\scripts\run_iadsk.ps1 -- new --dsk demo.dsk
.\scripts\run_iadsk.ps1 -- cat --dsk demo.dsk
.\scripts\run_iadsk.ps1 -Format json -- cat --dsk demo.dsk
```

## Códigos de error típicos

- `missing_option`
- `unknown_option`
- `unknown_command`
- `dsk_read_error`
- `dsk_invalid`
- `file_not_found`
- `file_exists`
- `protected_file`
- `removed_command`

## Alias soportados

- `import` -> `save`
- `export` -> `get`
- `rm` -> `era`
- `disassemble` -> `disasm`

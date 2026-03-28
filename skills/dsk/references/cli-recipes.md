# Recetas CLI de iaDSK

## Output Format

**BREAKING CHANGE:** A partir de ahora, iaDSK devuelve **JSON por defecto**.

- **Default:** JSON estructurado (optimizado para parseo automático por agentes IA)
- **Human-readable:** Añadir `--format markdown` para salida Markdown legible directamente
- **Compatibilidad:** Flag `--raw-json` obsoleto (siempre devuelve JSON sin formatear)

### Ejemplos de formato

```bash
# JSON (default) - Ideal para agentes IA
./scripts/run_iadsk.sh -- cat --dsk demo.dsk

# Markdown - Para lectura humana directa
./scripts/run_iadsk.sh --format markdown -- cat --dsk demo.dsk
```

```powershell
# JSON (default) - Ideal para agentes IA
.\scripts\run_iadsk.ps1 -- cat --dsk demo.dsk

# Markdown - Para lectura humana directa
.\scripts\run_iadsk.ps1 -Format markdown -- cat --dsk demo.dsk
```

**Para agentes IA:** Ejecutar comandos sin flags de formato, recibir JSON, parsear y presentar como Markdown al usuario.

## Patron general

1. Ejecutar wrappers de la skill (`run_iadsk.sh` o `run_iadsk.ps1`).
2. Por defecto, recibir salida JSON estructurada.
3. Para lectura humana directa:
   - shell: `--format markdown`
   - PowerShell: `-Format markdown`

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

## Modo interactivo con wrappers

Los wrappers `run_iadsk.sh` y `run_iadsk.ps1` detectan automáticamente el tipo de archivo y solicitan parámetros faltantes en modo interactivo:

### Añadir archivo binario con prompts

```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file loader.bin
```

**Interacción:**
```
Tipo de archivo AMSDOS:
  1) ascii   - Archivo de texto ASCII
  2) binary  - Archivo binario con cabecera AMSDOS
  3) raw     - Datos crudos sin cabecera

Selecciona tipo [2]: 2

Detectado archivo binario sin dirección de carga.

### Añadir archivo binario

Archivo: `loader.bin`

Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS.

Dirección de carga (--load) en hexadecimal: 0x8000

Dirección de ejecución (--exec) en hexadecimal.
OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos.

Dirección de ejecución (--exec): 0x8000
```

**Nota:** Si el usuario no ingresa una dirección de carga, el prompt se repetirá hasta que proporcione un valor válido.

### Añadir archivo de texto con prompts

```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file readme.txt
```

**Interacción:**
```
Tipo de archivo AMSDOS:
  1) ascii   - Archivo de texto ASCII
  2) binary  - Archivo binario con cabecera AMSDOS
  3) raw     - Datos crudos sin cabecera

Selecciona tipo [1]: 1
```

### Sobrescribir archivo existente

```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file programa.bas --type ascii
```

**Interacción:**
```
⚠️  El archivo 'programa.bas' ya existe en el disco.

¿Deseas sobrescribir? (s/n) [n]: s
```

### Modo no interactivo - ERROR si falta --load

```bash
echo "test" | ./scripts/run_iadsk.sh -- save --dsk demo.dsk --file program.bin
# ERROR: Archivos binarios requieren --load <dirección>.
# Ejemplo: --load 0x4000
```

**IMPORTANTE:** En modo no interactivo (pipes, automatización), los archivos binarios **requieren** especificar `--load` explícitamente. No hay valores por defecto.

### Especificar todos los parámetros (sin prompts)

```bash
./scripts/run_iadsk.sh -- save --dsk demo.dsk --file loader.bin \
  --type binary --load 0x8000 --exec 0x8000 --force
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

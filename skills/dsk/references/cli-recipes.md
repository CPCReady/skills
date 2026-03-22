# Recetas CLI de iadsk.py

## Patrón general

1. Ejecutar iadsk.py directamente con Python:
   ```bash
   python3 scripts/iadsk.py demo.dsk --cat
   ```
2. Salida Markdown por defecto (legible para humanos).
3. No hay modo JSON - solo Markdown.

## Requisitos

- Python 3.6+
- Solo stdlib (sin dependencias externas)

## Comandos frecuentes

### Crear y gestionar DSK

```bash
# Crear DSK vacío
python3 scripts/iadsk.py demo.dsk --new

# Listar archivos en disco
python3 scripts/iadsk.py demo.dsk --cat

# Ver espacio libre
python3 scripts/iadsk.py demo.dsk --free

# Verificar formato DSK
python3 scripts/iadsk.py demo.dsk --check

# Info detallada del disco
python3 scripts/iadsk.py demo.dsk --dump
```

### Añadir archivos

```bash
# Añadir binario con header AMSDOS
python3 scripts/iadsk.py demo.dsk --put-bin programa.bas

# Añadir archivo ASCII (conversión automática \n -> \r\n)
python3 scripts/iadsk.py demo.dsk --put-ascii readme.txt

# Añadir archivo raw (sin header)
python3 scripts/iadsk.py demo.dsk --put-raw datos.bin

# Binario con direcciones específicas
python3 scripts/iadsk.py demo.dsk --put-bin loader.bin --load-addr 0x4000 --start-addr 0x4000
```

### Gestionar archivos

```bash
# Ver contenido de archivo (texto)
python3 scripts/iadsk.py demo.dsk --list programa.bas

# Ver contenido como hex dump
python3 scripts/iadsk.py demo.dsk --list programa.bas --hex

# Extraer archivo por índice
python3 scripts/iadsk.py demo.dsk --get 0 --output ./programa.bas

# Extraer sin header AMSDOS
python3 scripts/iadsk.py demo.dsk --get 0 --no-header --output ./datos.bin

# Borrar archivo
python3 scripts/iadsk.py demo.dsk --era programa.bas
```

## Ejecución con wrappers (alternativa)

macOS/Linux:

```bash
./scripts/run_iadsk.sh -- demo.dsk --cat
./scripts/run_iadsk.sh -- demo.dsk --free
```

Windows:

```powershell
.\scripts\run_iadsk.ps1 -- demo.dsk --cat
.\scripts\run_iadsk.ps1 -- demo.dsk --free
```

## Versión

```bash
python3 scripts/iadsk.py --version
# Output: IADSK Tool Version 1.0.0
```

## Códigos de salida

- `0`: Éxito
- `1`: Error (archivo no encontrado, formato inválido, etc.)

## Notas

- Los nombres de archivo son case-insensitive
- Solo soporta discos single-sided (180KB)
- Máximo 64 entradas de directorio
- Máximo 16KB por archivo (automulti-entry para archivos más grandes)

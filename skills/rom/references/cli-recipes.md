# nocart CLI Recipes

## Comandos Generales

### Ayuda del comando
```bash
python3 scripts/nocart.py -h
```

### Chequear y Verificar ROM
```bash
python3 scripts/nocart.py check game.cpr
```

### Crear CPR desde cero con un disco source
```bash
python3 scripts/nocart.py create disk.dsk dest.cpr
```

### Crear Cartridge que lanza un AUTO-RUN en cadena
```bash
python3 scripts/nocart.py create disk.dsk dest.cpr --command 'run"disc"'
```

### Extraer sectores sueltos a una imagen DSK raw
```bash
python3 scripts/nocart.py dumpdsk dsk_interno.dsk cpr_external_dump.bin
```

## Tips para Agentes IA
- A diferencia de IaDSK o cdt, todos los outputs de logs y depuración (verbose) quedan codificados bajo las llaves `[tags]` e info extendida en el JSON.
- Ejecutar mediante `run_command` sin argumentos (ni stdin tty interactivo) causará error por ser `action` un argumento estrictamente posicional en Argparse y su correspondiente JSON error object indicándolo.

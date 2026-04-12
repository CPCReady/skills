# ROM (nocart) - Gestor de Cartuchos Amstrad GX-4000

Esta skill proporciona la herramienta `nocart` portada a Python, diseñada para la gestión interactiva de archivos de cartucho `.cpr`. Permite transformar disquetes `.dsk` en ROMs listas para su uso en la consola retro Amstrad GX-4000.

## Comandos Principales

```bash
python3 scripts/nocart.py create disk.dsk game.cpr --command 'run"disc"'
python3 scripts/nocart.py check game.cpr
python3 scripts/nocart.py dumpdsk disk.dsk dump.bin
```

## Características

- **Sin dependencias**: Se ejecuta directamente con Python 3 estándar.
- **Modo Interactivo**: Si omites la acción o el archivo de origen y destino, la herramienta te solicitará amigablemente los datos por consola.
- **Estructura JSON (AI Ready)**: En lugar de un registro (log) normal, la herramienta devuelve en todo momento un diccionario JSON válido con sus resultados.
- **Multicompatibilidad**: Puede manejar pistas MFM Extended DSK o MV-CPC.

## Requisitos

- **Python 3.6** o superior. No se requiere `pip install`.

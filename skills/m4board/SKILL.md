---
name: m4board
description: Control nativo y transferencia de archivos a placas Wi-Fi Amstrad M4Board. Interfaz remota para manejar CPCs físicos (reset, comandos, manipulacion de sdcard interna). La salida es JSON. Sustituto total de pyxfer.
---

# m4board

## Flujo recomendado

1. Usa los wrappers nativos (NO python directo) que instalarán el venv automáticamente:
   - macOS/Linux: `skills/m4board/scripts/run_m4board.sh <action> [args]`
   - Windows: `skills/m4board/scripts/run_m4board.ps1 <action> [args]`
2. Esta herramienta necesita **OBLIGATORIAMENTE** saber la IP del Amstrad M4Board objetivo.
   - Pásala bajo la variable global de entorno `M4BOARD_IP`.
   - Opcionalmente con la flag `--ip 192.168.1.XX`.
   - Si no haces ninguna de las dos, el script preguntará interactivamente bajo TTY.
3. Al igual que con *rom*, tú NUNCA debes inventar la IP de la placa. Preguntasela siempre al usuario si no dispones de ella.
4. Parsea el output JSON final en formato humano. Para listas como el action `ls`, formatea sus contenidos como directorios/archivos.

## Comandos disponibles

Sintaxis principal con wrappers:

```bash
run_m4board.sh [--ip XX.XX.XX.XX] <acción> [args]
```

### Lista principal de Acciones CLI (`argparse`)

- `reset_cpc` : Reinicia el ordenador Amstrad físico remotamente.
- `reboot_m4` : Reinicia solo la placa lógica del M4 Board.
- `upload <localfile> [dest]` : Sube un archivo en el CPC. (Defecto `/`).
- `download <cpcfile>` : Descarga un archivo presente en la tarjeta SD de la M4Board localmente.
- `execute <cpcfile>` : Obliga a cargar mediante AMSDOS y ejecutar un fichero.
- `run <local_file>` : Atajo hiper-desarrollador que realiza un upload a `/tmp` seguido de una ejecución autómata.
- `mkdir <folder>` : Crea un directorio.
- `cd <folder>` : Fija el path activo real de la M4Board.
- `rm <cpcfile>` : Elimina ficheros de forma permanente en la placa física.
- `delrom <id>` / `putrom <localfile> <id> <name>`: Inyección y borrado de ROMs.
- `ls [folder]`: Lista estructura de formato web de directorios empaquetada en el json final.

## Respuestas JSON

Ejemplo de `status` sobre action ejecutada exitósamente de `ls`:
```json
{
  "status": "ok",
  "action": "ls",
  "ip": "192.168.1.15",
  "data": {
    "directory": "/",
    "listing": "DIR listing of \\m4\\nfile.bin 1024\\n"
  }
}
```

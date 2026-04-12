# M4Board - Control Remoto WIFI

Herramienta diseñada para actuar directamente sobre placas M4Board en máquinas físicas Amstrad CPC. Reemplaza el antiguo script `pyxfer` con una versión puramente de Python estándar, modernizada con JSON outputs listos para Inteligencia Artificial.

## Comandos y Wrappers
**No debes requerir de un entorno externo global**. La skill se encierra en un *VENV* local para pre-instalar `requests`. Invócalo en tus scripts usando el auto-empaquetador:

`./scripts/run_m4board.sh --ip 192.168.1.15 upload mi_juego.bin`

## Acciones de Sistema

- `reset_cpc` / `reboot_m4`: Control de hardware y tarjeta sub-lógica.
- `upload` / `download` / `rm`: Edición cruda de la SD card remota.
- `putrom` / `delrom`: Parcheo en caliente del listado ROM activo del ID0 al ID31 de la placa base interna.
- `execute` / `run`: Automatizan subir por red y obligar a AMSDOS local de la máquina vieja a ejecutar un fichero instantáneamente usando `config.cgi`.
- `mkdir` / `cd` / `ls`: Control del sistema de archivos MS-DOS.
- `pause`. Manda orden ACIA.

Todo error de red es tratado y encajado limpiamente dentro del formato JSON, lo cual garantiza que herramientas y scripts externos no colapsarán.

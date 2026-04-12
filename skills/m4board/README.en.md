# M4Board - WIFI Remote Control

Tool designed to act directly on M4Board plates in physical Amstrad CPC machines. Replaces the old `pyxfer` script with a purely modernized Python standard version, with JSON outputs ready for Artificial Intelligence.

## Commands and Wrappers
**You should not require a global external environment**. The skill is enclosed in a local *VENV* to pre-install `requests`. Call it in your scripts using the auto-packager:

`./scripts/run_m4board.sh --ip 192.168.1.15 upload my_game.bin`

## System Actions

- `reset_cpc` / `reboot_m4`: Hardware and sub-logic card control.
- `upload` / `download` / `rm`: Raw editing of the remote SD card.
- `putrom` / `delrom`: Hot patching of the active ROM list from ID0 to ID31 of the internal motherboard.
- `execute` / `run`: Automatizan subir por red y obligar a AMSDOS local de la máquina vieja a ejecutar un fichero instantáneamente usando `config.cgi`.
- `mkdir` / `cd` / `ls`: Control del sistema de archivos MS-DOS.
- `pause`. Sends ACIA command.

Any network error is cleanly packaged within the JSON format, which guarantees that external tools and scripts will not collapse.

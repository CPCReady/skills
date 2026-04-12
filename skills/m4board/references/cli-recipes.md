# m4board CLI Recipes

## Configurar el ENTORNO (Global Linux/Mac)
En tu ~/.bashrc o sesión de Terminal:
```bash
export M4BOARD_IP="192.168.1.33"
```

## Operaciones Subcomandos Standard

### Listar Ficheros
```bash
./scripts/run_m4board.sh ls /juegos
```

### Reset Completo por red
```bash
./scripts/run_m4board.sh reboot_m4 && ./scripts/run_m4board.sh reset_cpc
```

### Ejecutar o jugar a un juego (Hyper-developer mode)
`run` sube el `.bin` o `.bas` explícitamente a `/tmp` en M4Board y automáticamente llama a AMSDOS en el Amstrad físico para ejecutar el temporal.

```bash
./scripts/run_m4board.sh run ./game.bin
```

### Inyectar ROM Personalizada
```bash
./scripts/run_m4board.sh putrom parados.rom 1 "ParaDOS Final"
```

## Troubleshooting
Si `run_m4board.sh` colapsa con un *'Module requests no encontrado'*: Esto significa que la ruta al ejecutable es diferente a como espera bash. Borra ocultos `.venv` e intenta relanzar `run_m4board.sh`.

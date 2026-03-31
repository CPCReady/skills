# Recetas CLI — Retro Virtual Machine 2

Referencia completa de uso del wrapper `run_rvm.sh` / `run_rvm.ps1` para el emulador
**Retro Virtual Machine 2 v2.0 BETA-1 r7**.

---

## Requisito previo

Definir la variable de entorno `RETRO_VIRTUAL_MACHINE_PATH` apuntando al binario de RVM:

```bash
# macOS
export RETRO_VIRTUAL_MACHINE_PATH="/Applications/Retro Virtual Machine 2.app/Contents/MacOS/Retro Virtual Machine 2"

# Linux
export RETRO_VIRTUAL_MACHINE_PATH="/usr/local/bin/rvm2"
```

```powershell
# Windows
$env:RETRO_VIRTUAL_MACHINE_PATH = "C:\Program Files\Retro Virtual Machine 2\rvm2.exe"
```

---

## Patrón general

```bash
./scripts/run_rvm.sh [opciones] [<archivo>]
```

```powershell
.\scripts\run_rvm.ps1 [opciones] [<archivo>]
```

RVM se lanza en **segundo plano** — el wrapper termina inmediatamente.

---

## Opciones del wrapper

| Opción (Bash) | Opción (PowerShell) | Descripción |
|---------------|---------------------|-------------|
| `--machine <id>` / `-m <id>` | `-Machine <id>` | Máquina CPC a emular |
| `--warp` / `-w` | `-Warp` | Modo acelerado (sin límite de velocidad) |
| `--noshader` / `-ns` | `-NoShader` | Desactivar shader de pantalla |
| `--command <texto>` / `-c <texto>` | `-Command <texto>` | Enviar teclas al intérprete BASIC al arrancar |
| `--width <px>` / `-wi <px>` | `-Width <px>` | Ancho de ventana (mínimo 700 píxeles) |
| `--play` / `-p` | `-Play` | Auto play de cinta al inicio |
| `--` | `--` | Pass-through: el resto de argumentos van directamente a RVM |
| `--help` / `-h` | — | Mostrar ayuda del wrapper |

---

## Máquinas disponibles

| ID | Modelo | RAM | Almacenamiento | Uso típico |
|----|--------|-----|----------------|------------|
| `cpc464` | Amstrad CPC 464 | 64K | Cassette | Juegos en cinta |
| `cpc664` | Amstrad CPC 664 | 64K | Disco 3" | Juegos en disco (raro) |
| `cpc6128` | Amstrad CPC 6128 | 128K | Disco 3" | Juegos en disco, demos |

**Por defecto según archivo:**
- `.dsk` → `cpc6128`
- `.cdt` / `.tzx` → `cpc464`
- `.bin` / `.sna` / `.z80` / sin archivo → **pregunta interactiva**

---

## Recetas frecuentes

### Lanzar imagen de disco

```bash
./scripts/run_rvm.sh game.dsk
# Equivale a: RVM --boot=cpc6128 --insert game.dsk
```

```powershell
.\scripts\run_rvm.ps1 game.dsk
```

### Lanzar cinta CDT

```bash
./scripts/run_rvm.sh demo.cdt
# Equivale a: RVM --boot=cpc464 --insert demo.cdt
```

```powershell
.\scripts\run_rvm.ps1 demo.cdt
```

### Lanzar cinta TZX

```bash
./scripts/run_rvm.sh demo.tzx
# Equivale a: RVM --boot=cpc464 --insert demo.tzx
```

### Lanzar con máquina específica

```bash
# Usar CPC 464 con un juego en disco
./scripts/run_rvm.sh --machine cpc464 game.dsk
```

```powershell
.\scripts\run_rvm.ps1 -Machine cpc664 game.dsk
```

### Lanzar en modo acelerado (warp)

```bash
./scripts/run_rvm.sh --warp game.dsk
./scripts/run_rvm.sh --warp demo.cdt
```

```powershell
.\scripts\run_rvm.ps1 -Warp game.dsk
```

### Enviar comando BASIC al arrancar

```bash
# Ejemplo: ejecutar RUN automáticamente
./scripts/run_rvm.sh --command 'run"' demo.cdt
```

```powershell
.\scripts\run_rvm.ps1 -Command 'run"' demo.cdt
```

### Arrancar en modo standalone (sin archivo)

```bash
# El wrapper preguntará qué máquina usar
./scripts/run_rvm.sh
```

```powershell
.\scripts\run_rvm.ps1
```

### Cargar binario .bin (requiere prompts)

```bash
# El wrapper pedirá: máquina, dirección de carga, dirección de salto
./scripts/run_rvm.sh programa.bin
```

En automatización, proporcionar todos los parámetros con pass-through:

```bash
./scripts/run_rvm.sh --machine cpc6128 -- --boot=cpc6128 --load=0x4000 programa.bin --jump=0x4000
```

### Cargar snapshot

```bash
# El wrapper preguntará qué máquina usar
./scripts/run_rvm.sh save.sna
./scripts/run_rvm.sh save.z80
```

Con máquina explícita:

```bash
./scripts/run_rvm.sh --machine cpc6128 save.sna
```

### Ancho de ventana personalizado

```bash
./scripts/run_rvm.sh --width 1400 game.dsk
```

```powershell
.\scripts\run_rvm.ps1 -Width 1400 game.dsk
```

### Pass-through directo a RVM

Para usar flags de RVM no cubiertos por el wrapper:

```bash
./scripts/run_rvm.sh -- --boot=cpc6128 --insert game.dsk --warp --noshader
./scripts/run_rvm.sh -- --boot=cpc464 --insert tape.cdt --play --command 'run"'
./scripts/run_rvm.sh -- --boot=cpc6128 --dandanator romset.zip
```

```powershell
.\scripts\run_rvm.ps1 -- --boot=cpc6128 --insert game.dsk --warp
```

---

## Flags directos de RVM (referencia)

Estos flags se pasan directamente al binario de RVM mediante `--`:

| Flag | Alias | Descripción |
|------|-------|-------------|
| `--boot=<id>` | `-b=<id>` | Arrancar máquina CPC (cpc464, cpc664, cpc6128) |
| `--insert <archivo>` | `-i <archivo>` | Insertar cinta (.cdt/.tzx) o disco (.dsk) |
| `--load=<addr> <archivo>` | `-l=<addr>` | Cargar binario en dirección de memoria |
| `--jump=<addr>` | `-j=<addr>` | Saltar a dirección de memoria tras cargar |
| `--command=<texto>` | `-c=<texto>` | Enviar teclas al intérprete BASIC |
| `--play` | `-p` | Auto play de cinta al arrancar |
| `--warp` | `-w` | Modo acelerado |
| `--snapshot <archivo>` | `-s <archivo>` | Cargar snapshot .sna o .z80 |
| `--dandanator <archivo>` | `-d <archivo>` | Cargar romset en dandanator virtual |
| `--width=<px>` | `-wi=<px>` | Ancho de ventana (mínimo 700) |
| `--noshader` | `-ns` | Desactivar shader |
| `--list` | `-li` | Listar máquinas disponibles |
| `--help` | `-h` | Mostrar ayuda de RVM |
| `--nocolor` | `-nc` | Desactivar colores en la salida |

---

## Códigos de error del wrapper

| Código | Causa |
|--------|-------|
| `1` | `RETRO_VIRTUAL_MACHINE_PATH` no definida |
| `1` | Binario de RVM no encontrado o sin permisos de ejecución |
| `1` | Versión de RVM no compatible (requerida: v2.0 BETA-1 r7) |
| `1` | Archivo de entrada no encontrado |
| `1` | Extensión de archivo no reconocida |
| `1` | Modo no interactivo con parámetros obligatorios faltantes |

---

## Troubleshooting

**RVM no se abre / no hace nada:**
- Verificar que `RETRO_VIRTUAL_MACHINE_PATH` apunta al binario correcto.
- Comprobar permisos de ejecución del binario.
- En macOS: verificar que la app no está bloqueada por Gatekeeper.

**Error de versión:**
- Descargar e instalar RVM v2.0 BETA-1 r7 desde https://www.retrovirtualmachine.org

**Cinta no arranca sola:**
- Añadir `--command 'run"'` para enviar el comando BASIC automáticamente.
- O usar `--play` para activar el reproductor automático de cinta.

**Disco no carga el menú:**
- Algunos juegos requieren teclar `CAT` o `RUN"DISC` manualmente.
- Usar `--command 'run"disc'` o el comando específico del juego.

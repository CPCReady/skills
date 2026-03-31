---
name: retrovirtualmachine
description: Lanzar y gestionar el emulador Retro Virtual Machine 2 (v2.0 BETA-1 r7) para Amstrad CPC. Usar cuando el usuario quiera ejecutar imágenes .dsk, .cdt, .tzx, .bin, .sna o .z80 en el emulador, arrancar el emulador en modo standalone, o pasar argumentos avanzados a RVM (warp, shader, comandos BASIC, snapshots).
---

# retrovirtualmachine

Skill para lanzar el emulador **Retro Virtual Machine 2** (RVM) con imágenes de Amstrad CPC.

**Versión requerida:** `v2.0 BETA-1 r7`  
**Binario:** variable de entorno `RETRO_VIRTUAL_MACHINE_PATH` (obligatoria)

---

## Flujo recomendado

1. Verificar que `RETRO_VIRTUAL_MACHINE_PATH` está definida → error claro si no.
2. Ejecutar el wrapper nativo del sistema:
   - macOS / Linux: `scripts/run_rvm.sh`
   - Windows: `scripts/run_rvm.ps1`
3. El wrapper verifica automáticamente la versión de RVM al arrancar.
4. El wrapper detecta el tipo de archivo por extensión y aplica la máquina por defecto.
5. Si faltan datos (máquina, dirección de carga, dirección de salto), el wrapper los pide interactivamente.
6. RVM se lanza en **segundo plano** — el wrapper termina inmediatamente.

---

## Requisito: variable de entorno

```bash
# macOS / Linux
export RETRO_VIRTUAL_MACHINE_PATH="/Applications/Retro Virtual Machine 2.app/Contents/MacOS/Retro Virtual Machine 2"
```

```powershell
# Windows
$env:RETRO_VIRTUAL_MACHINE_PATH = "C:\Program Files\Retro Virtual Machine 2\rvm2.exe"
```

Si la variable no está definida, el wrapper falla con:
```
ERROR: Variable de entorno RETRO_VIRTUAL_MACHINE_PATH no definida.
```

---

## Comportamiento por tipo de archivo

| Extensión | Máquina por defecto | Argumento RVM | Notas |
|-----------|--------------------|------------------------------------|-------|
| `.dsk` | `cpc6128` | `--boot=cpc6128 --insert <archivo>` | CPC 6128 con disco |
| `.cdt` | `cpc464` | `--boot=cpc464 --insert <archivo>` | CPC 464 con cinta |
| `.tzx` | `cpc464` | `--boot=cpc464 --insert <archivo>` | Cinta TZX |
| `.bin` | **preguntar** | `--boot=<m> --load=<addr> <archivo> --jump=<addr>` | Pide máquina, load y jump |
| `.sna` / `.z80` | **preguntar** | `--boot=<m> --snapshot <archivo>` | Pide máquina |
| (sin archivo) | **preguntar** | `--boot=<m>` | Standalone vacío |

El usuario puede sobrescribir siempre la máquina con `--machine` / `-m`.

---

## Máquinas CPC disponibles

| ID | Modelo | RAM | Almacenamiento |
|----|--------|-----|----------------|
| `cpc464` | Amstrad CPC 464 | 64K | Cassette |
| `cpc664` | Amstrad CPC 664 | 64K | Disco 3" |
| `cpc6128` | Amstrad CPC 6128 | 128K | Disco 3" |

---

## Ejecutar por sistema operativo

macOS / Linux:

```bash
# Lanzar disco (máquina por defecto: cpc6128)
./scripts/run_rvm.sh game.dsk

# Lanzar cinta (máquina por defecto: cpc464)
./scripts/run_rvm.sh demo.cdt

# Especificar máquina explícitamente
./scripts/run_rvm.sh --machine cpc464 game.dsk

# Modo acelerado
./scripts/run_rvm.sh --warp game.dsk

# Sin archivo (modo standalone - pregunta máquina)
./scripts/run_rvm.sh

# Pass-through directo a RVM
./scripts/run_rvm.sh -- --boot=cpc6128 --insert game.dsk --warp
```

Windows:

```powershell
# Lanzar disco
.\scripts\run_rvm.ps1 game.dsk

# Lanzar cinta
.\scripts\run_rvm.ps1 demo.cdt

# Especificar máquina
.\scripts\run_rvm.ps1 -Machine cpc464 game.dsk

# Modo acelerado
.\scripts\run_rvm.ps1 -Warp game.dsk

# Pass-through directo a RVM
.\scripts\run_rvm.ps1 -- --boot=cpc6128 --insert game.dsk --warp
```

---

## Prompts interactivos

Los wrappers solicitan información al usuario cuando es necesaria y no se proporcionó:

### Selección de máquina CPC

**Cuándo:** Archivo `.bin`, `.sna`, `.z80` o modo sin archivo, y el usuario no especificó `--machine`.

```
### Máquina CPC

  1) cpc464   - Amstrad CPC 464 (cassette, 64K RAM)
  2) cpc664   - Amstrad CPC 664 (disco, 64K RAM)
  3) cpc6128  - Amstrad CPC 6128 (disco, 128K RAM)

Selecciona máquina [1-3]:
```

- El prompt se repite hasta que el usuario seleccione una opción válida.
- **En modo no interactivo (pipes/automatización):** falla con error.

### Dirección de carga y salto (solo archivos `.bin`)

**Cuándo:** Archivo con extensión `.bin` sin `--load` o `--jump` explícitos.

```
### Cargar archivo binario

Archivo: `programa.bin`
Para archivos binarios es OBLIGATORIO indicar la dirección de carga y de salto.

Dirección de carga (--load) (hexadecimal): 
Dirección de salto (--jump) (hexadecimal): 
```

- Ambas direcciones son **obligatorias** — el prompt se repite hasta recibir un valor.
- **En modo no interactivo:** falla con error explícito.

---

## Modo no interactivo

Cuando stdin no es un terminal (pipes, scripts, CI), los wrappers **no usan valores por defecto**:

- Máquina: **FALLA si es necesaria y no se proporcionó** con `--machine`.
- Direcciones `.bin`: **FALLA** si no se proporcionan explícitamente.

Ejemplo de automatización correcta:

```bash
./scripts/run_rvm.sh --machine cpc464 demo.cdt
./scripts/run_rvm.sh --machine cpc6128 -- --boot=cpc6128 --insert game.dsk --warp
```

---

## CRITICAL: Comportamiento del agente

**NUNCA ASUMIR MÁQUINAS NI DIRECCIONES DE MEMORIA**

Cuando el usuario solicita lanzar un archivo con RVM, el agente **DEBE**:

1. **NO proporcionar** máquina por defecto para `.bin`, `.sna`, `.z80` — dejar que el wrapper la pregunte.
2. **NO proporcionar** `--load` ni `--jump` para archivos `.bin` — dejar que el wrapper los solicite.
3. **Ejecutar el wrapper sin esos parámetros** para activar los prompts interactivos.
4. **SIEMPRE pasar `--close-existing`** al wrapper — el agente nunca tiene TTY, sin este flag las instancias abiertas se ignoran silenciosamente.

**INCORRECTO (NO HACER ESTO):**
```bash
./scripts/run_rvm.sh --machine cpc6128 programa.bin --load 0x4000 --jump 0x4000
./scripts/run_rvm.sh game.dsk   # sin --close-existing
```

**CORRECTO:**
```bash
./scripts/run_rvm.sh --close-existing programa.bin
./scripts/run_rvm.sh --close-existing game.dsk
```

**Excepciones:** Solo proporcionar `--machine`, `--load`, `--jump` si:
- El usuario los especificó explícitamente en su solicitud.
- Se está ejecutando en modo no interactivo (automatización).

---

## Presenting results to the user

RVM es una aplicación GUI — no produce salida estructurada por línea de comandos.

El agente **DEBE**:

1. **Ejecutar el wrapper** silenciosamente (background).
2. **Confirmar al usuario** con un mensaje Markdown conciso:

```markdown
**Retro Virtual Machine** iniciado.

| Campo | Valor |
|-------|-------|
| Archivo | `game.dsk` |
| Máquina | cpc6128 |
| Modo | Normal |
```

3. **NO mostrar** la ruta del binario, el comando construido ni argumentos internos.
4. **Si hubo error** (versión incorrecta, archivo no encontrado, variable no definida): mostrar solo el mensaje de error relevante al usuario, sin el stack trace completo.

---

## Verificación de versión

El wrapper comprueba automáticamente la versión en cada ejecución:

```
ERROR: Versión de Retro Virtual Machine no compatible.
  Requerida : v2.0 BETA-1 r7
  Detectada : <versión instalada>
```

Si el usuario recibe este error, debe actualizar o instalar la versión correcta de RVM.

---

## Recursos

- `scripts/run_rvm.sh`: wrapper Unix (macOS / Linux).
- `scripts/run_rvm.ps1`: wrapper Windows PowerShell.
- `references/cli-recipes.md`: referencia completa de todos los flags de RVM.
- [Retro Virtual Machine](https://www.retrovirtualmachine.org): sitio oficial.

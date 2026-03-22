# Amstrad CPC Skills

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/CPCReady/skills)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Amstrad CPC](https://img.shields.io/badge/Amstrad-CPC-orange)](https://www.cpcwiki.eu/)
[![Skills](https://img.shields.io/badge/skills.sh-available-purple)](https://skills.sh)

> Skills profesionales para desarrollo de retro computing en Amstrad CPC

---

## Instalación

Instalar todas las skills:

```bash
npx skills add CPCReady/skills
```

Instalar una skill específica:

```bash
npx skills add CPCReady/skills/dsk   # Discos
npx skills add CPCReady/skills/cdt   # Cintas
```

---

## Skills Disponibles

### 🖥️ dsk - Editor de Imágenes de Disco iaDSK

Automatización para iaDSK, una herramienta de línea de comandos para crear, editar y gestionar imágenes de disco `.dsk` de Amstrad CPC.

#### Características
- Soporte multiplataforma (Windows, macOS, Linux)
- Binarios precompilados incluidos
- Salida legible en formato Markdown
- Modo JSON para automatización
- Soporte para arquitecturas x64 y ARM64

#### Casos de Uso
- Crear o editar imágenes de disco .dsk
- Gestionar archivos en discos de Amstrad CPC
- Extraer o inyectar archivos en imágenes de disco
- Trabajar con proyectos de retro computing

#### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `help` | Mostrar ayuda |
| `new` | Crear nuevo disco .dsk |
| `cat` | Listar archivos del disco |
| `free` | Mostrar espacio libre |
| `save` | Guardar archivo en disco |
| `get` | Extraer archivo del disco |
| `era` | Eliminar archivo del disco |
| `list` | Mostrar contenido como lista |
| `basic` | Mostrar archivo BASIC |
| `ascii` | Mostrar archivo ASCII |
| `hex` | Mostrar contenido en hexadecimal |
| `disasm` | Desensamblar código Z80 |
| `dams` | Ensamblar con DAMS |

#### Tipos de Archivo Soportados

| Tipo | Código | Uso |
|------|--------|-----|
| ASCII | `A` | Texto, documentos |
| Binario | `B` | Ejecutables, datos |
| Raw | `R` | Datos sin procesar |

#### Ejemplos de Prompts

```
"Crea un nuevo disco llamado game.dsk y añade el archivo loader.bin"
"Lista todos los archivos del disco retro.dsk"
"Extrae todos los archivos de backup.dsk a la carpeta extraction"
"Muestra el contenido BASIC del archivo MAIN.BAS"
"Desensambla el archivo SPRITE.BIN"
```

---

## Ejemplos Detallados

### 📋 Operaciones Básicas

#### Mostrar ayuda
```
"Muéstrame la ayuda de iaDSK"
"¿Qué comandos están disponibles en iaDSK?"
```

#### Crear un nuevo disco
```
"Crea un nuevo disco llamado project.dsk"
"Haz una nueva imagen DSK llamada backup.dsk"
```

#### Listar contenido del disco (catálogo)
```
"Muéstrame qué hay en el disco game.dsk"
"Lista todos los archivos en retro.dsk"
"¿Qué archivos hay en el disco collection.dsk?"
```

#### Comprobar espacio libre
```
"¿Cuánto espacio libre hay en demo.dsk?"
"Comprueba el espacio disponible en backup.dsk"
```

---

### 💾 Operaciones con Archivos

#### Guardar archivos de texto ASCII
```
"Añade el archivo readme.txt al disco docs.dsk como ASCII"
"Guarda intro.txt en game.dsk como archivo de texto"
"Importa el archivo de texto credits.txt en project.dsk"
```

#### Guardar archivos binarios (ejecutables)
```
"Añade loader.bin a game.dsk como binario con dirección de carga 0x8000 y ejecución en 0x8000"
"Guarda sprite.bin en graphics.dsk como binario, carga en 40000, ejecuta en 40000"
"Importa main.bin en project.dsk como binario con carga y ejecución ambos en 32768"
```

#### Guardar archivos de datos raw
```
"Añade tileset.dat a graphics.dsk como datos raw"
"Guarda music.raw en audio.dsk como tipo raw"
```

#### Guardar con nombre AMSDOS personalizado
```
"Guarda loader.bin en game.dsk como binario con el nombre BOOT.BIN, carga 0x4000, ejecuta 0x4000"
"Añade main.bas a project.dsk como ASCII con el nombre START.BAS"
```

#### Extraer archivos del disco
```
"Extrae program.bas de game.dsk a ./extracted/"
"Obtén todos los archivos de backup.dsk y guárdalos en la carpeta output"
"Exporta loader.bin de retro.dsk a ./binaries/loader.bin"
```

#### Eliminar archivos del disco
```
"Elimina el archivo old.bas de project.dsk"
"Borra temp.bin de game.dsk"
"Quita el archivo unused.dat de backup.dsk"
```

---

### 🔍 Ver Contenido de Archivos

#### Ver archivo como lista raw
```
"Lista el contenido de program.bas de game.dsk"
"Muéstrame el contenido raw de data.bin en project.dsk"
```

#### Ver programas BASIC
```
"Muéstrame el programa BASIC main.bas de game.dsk"
"Muestra loader.bas de retro.dsk como BASIC con líneas separadas"
"Ver el contenido BASIC de menu.bas en project.dsk, separado por líneas"
```

#### Ver archivos de texto ASCII
```
"Muestra el contenido ASCII de readme.txt de docs.dsk"
"Muestra intro.txt de game.dsk como texto"
```

#### Ver archivos en hexadecimal
```
"Muestra sprite.bin de graphics.dsk en hexadecimal"
"Muestra el volcado hex de loader.bin en game.dsk"
"Ver data.bin de backup.dsk en formato hex"
```

#### Desensamblar archivos binarios Z80
```
"Desensambla loader.bin de game.dsk"
"Muestra el ensamblador Z80 de sprite.bin en graphics.dsk"
"Desensambla main.bin de retro.dsk y muéstrame el código"
```

#### Ver código fuente DAMS
```
"Muestra el código fuente DAMS de sprite.asm de project.dsk"
"Muestra routines.dam de game.dsk como ensamblador DAMS"
```

---

### 📼 cdt - Toolkit de cintas ia2cdt

Automatiza el nuevo script Python ia2cdt para crear y validar imágenes de cassette Amstrad CPC (`.cdt`/`.tzx`). Todo se ejecuta con Python 3, sin instaladores ni binarios externos.

#### Características
- CLI con subcomandos (`new`, `save`, `cat`, `check`).
- Métodos de datos avanzados: bloques estándar, headerless, Spectrum, splits 2K y 1B.
- Control de baudios 1000–6000 y pausas personalizadas.
- Salidas Markdown y JSON listas para documentación o CI.
- Lectura y escritura en una sola herramienta.

#### Casos de Uso
- Generar cintas multi-etapa (loader rápido + payload binario).
- Inyectar pantallas o recursos sin cabecera AMSDOS.
- Exportar inventarios JSON para pipelines de liberación.
- Validar `.cdt` de terceros antes de distribuirlos.

#### Resumen de Comandos

| Comando | Descripción |
|---------|-------------|
| `new <cdt>` | Crea una cinta vacía |
| `save <cdt> --file <ruta>` | Añade archivo con parámetros avanzados |
| `cat <cdt> [--format json]` | Lista los bloques |
| `check <cdt>` | Comprueba formato y CRC |

#### Métodos de datos

| Método | Nombre | Notas |
|--------|--------|-------|
| `0` | Blocks | Formato CPC con cabecera AMSDOS |
| `1` | Headerless | Bloque CPC sin cabecera (RAM directa) |
| `2` | Spectrum | Formato estándar ZX (flag + checksum) |
| `3` | Two blocks 2K | 2048 bytes iniciales + resto |
| `4` | Two blocks 1B | Primer byte aislado + resto |

#### Ejemplos de Prompts
```
"Crea una cinta loader.cdt y añade loader.bas a 6000 baudios"
"Añade main.bin a build.cdt con load=0x4000 exec=0x4000"
"Inserta screen.scr en demo.cdt como headerless en 0xC000"
"Muestra el catálogo de retro.cdt en formato JSON"
"Valida la integridad de competition.cdt"
```

---

### 🎯 Flujos de Trabajo Complejos

#### Crear disco y añadir múltiples archivos
```
"Crea un nuevo disco game.dsk, luego añade loader.bin como binario (carga 0x8000, ejecuta 0x8000), 
añade main.bas como ASCII, y añade sprites.bin como binario (carga 0x4000, ejecuta 0x4000)"
```

#### Flujo de respaldo
```
"Muéstrame todos los archivos en original.dsk, luego extráelos todos a ./backup/, 
después crea un nuevo disco copy.dsk y añade todos los archivos extraídos"
```

#### Inspeccionar y modificar
```
"Muestra el contenido de project.dsk, comprueba el espacio libre, 
luego elimina old.bas y temp.bin, y añade new.bas como ASCII"
```

#### Flujo de desarrollo
```
"Crea dev.dsk, añade loader.bin (binario, carga 0x8000, ejecuta 0x8000), 
añade game.bas (ASCII), añade sprites.bin (binario, carga 0xC000), 
luego muéstrame el catálogo final y el espacio libre"
```

#### Análisis de binarios
```
"Extrae loader.bin de game.dsk, muéstrame su volcado hex, 
luego desensámblalo para ver el código ensamblador Z80"
```

---

### 🔧 Opciones Avanzadas

#### Usar nombre de archivo AMSDOS personalizado (formato 8.3)
```
"Guarda mi_archivo_largo.bin en game.dsk como LOADER.BIN con carga 0x8000 y ejecuta 0x8000"
```

#### Especificar número de usuario (0-15)
```
"Guarda config.dat en disk.dsk como ASCII con número de usuario 5"
"Añade hidden.bin a secret.dsk como binario (carga 0x4000, ejecuta 0x4000) con usuario 7"
```

#### Establecer protección de solo lectura
```
"Guarda important.bas en backup.dsk como ASCII y márcalo como solo lectura"
"Añade system.bin a boot.dsk como binario (carga 0x4000, ejecuta 0x4000) con protección de solo lectura"
```

#### Establecer atributo de archivo del sistema
```
"Guarda kernel.bin en os.dsk como binario (carga 0x0000, ejecuta 0x0000) y márcalo como archivo del sistema"
```

---

### 📦 Operaciones por Lotes

#### Procesar múltiples discos
```
"Muéstrame el catálogo de disk1.dsk, disk2.dsk y disk3.dsk"
"Comprueba el espacio libre en todos los discos: game1.dsk, game2.dsk, game3.dsk"
```

#### Organizar por tipo de archivo
```
"Extrae todos los archivos .BAS de project.dsk a ./basic/, 
todos los archivos .BIN a ./binaries/, y todos los archivos .TXT a ./text/"
```

---

### 🚨 Ejemplos de Manejo de Errores

#### Cuando el disco no existe
```
Usuario: "Muestra el contenido de missing.dsk"
Agente: Mostrará mensaje de error indicando que no se encontró el archivo de disco
```

#### Cuando el archivo no existe en el disco
```
Usuario: "Extrae nonexistent.bas de game.dsk"
Agente: Mostrará error indicando que el archivo no está en el disco
```

#### Cuando el archivo ya existe en el disco
```
Usuario: "Añade loader.bin a game.dsk"
Agente: Si LOADER.BIN ya existe, mostrará error. 
        El usuario puede entonces eliminar el archivo antiguo primero o usar un nombre diferente.
```

---

### 💡 Consejos

- **Nomenclatura de archivos**: AMSDOS usa formato 8.3 (8 caracteres nombre, 3 caracteres extensión). Los nombres largos se truncan automáticamente.
- **Direcciones**: Se pueden especificar en decimal (32768) o hexadecimal (0x8000 u 8000h)
- **Números de usuario**: Rango 0-15, por defecto es 0. Usuario 0 es estándar, otros pueden organizar archivos.
- **Protección**: Los atributos de solo lectura y sistema ayudan a proteger archivos importantes.
- **Capacidad del disco**: Los discos CPC estándar contienen 178 KB (formato Data) o 169 KB (formato System)
- **Tipos de archivo**: ASCII para texto/BASIC, Binario para ejecutables, Raw para datos puros

---

## Uso

### Con OpenCode/Claude Code

Simplemente menciona la skill en tu petición:

```
"Usa la skill dsk para mostrarme qué hay en esta imagen de disco"
```

El agente automáticamente:
1. Verificará si iaDSK está disponible
2. Instalará iaDSK si es necesario (usando scripts específicos de cada plataforma)
3. Ejecutará la operación solicitada
4. Devolverá los resultados en formato legible

### Instalación Específica por Plataforma

La skill dsk incluye scripts de instalación automatizados:

**macOS / Linux:**
```bash
./skills/dsk/scripts/install_iadsk.sh
```

**Windows:**
```powershell
.\skills\dsk\scripts\install_iadsk.ps1
```

### Formatos de Salida

- **Markdown** (por defecto): Salida legible para uso interactivo
- **JSON**: Añade `--format json` para procesamiento programático

---

## Estructura del Repositorio

```
CPCReady/skills/
├── .claude-plugin/          # Configuración del marketplace
│   └── marketplace.json
├── skills/                  # Skills individuales
│   └── dsk/                # Editor de discos iaDSK
│       ├── SKILL.md        # Instrucciones de la skill para agentes
│       ├── agents/         # Agentes auxiliares
│       ├── assets/         # Binarios precompilados de iaDSK
│       ├── references/     # Documentación de iaDSK
│       └── scripts/        # Scripts de instalación y ejecución
├── .gitignore
├── LICENSE                 # Licencia MIT
├── README.md              # Este archivo
└── plugin.json            # Metadatos del plugin
```

---

## Plataformas Soportadas

Estas skills funcionan con:

- [OpenCode](https://opencode.ai/)
- [Claude Code](https://claude.com/product/claude-code)
- [GitHub Copilot](https://github.com/features/copilot)
- [Cursor](https://cursor.sh)
- [Windsurf](https://codeium.com/windsurf)
- [Cline](https://cline.bot/)
- Cualquier otro agente que soporte el [estándar Agent Skills](https://agentskills.io)

---

## Acerca de Amstrad CPC

El Amstrad CPC fue un ordenador personal doméstico lanzado en 1984, muy popular en Europa. Utiliza disquetes de 3 pulgadas y tiene una vasta biblioteca de software clásico. Estas skills ayudan a los desarrolladores modernos a trabajar con imágenes de disco CPC y herramientas de desarrollo.

---

## Resolución de Problemas

### Error: "iaDSK not found"

La skill incluye binarios embebidos. El script de instalación debería ejecutarse automáticamente, pero puedes activarlo manualmente:

```bash
# macOS/Linux
./skills/dsk/scripts/install_iadsk.sh

# Windows
.\skills\dsk\scripts\install_iadsk.ps1
```

### Error: "Permission denied"

Haz que los scripts sean ejecutables:

```bash
chmod +x skills/dsk/scripts/install_iadsk.sh
chmod +x skills/dsk/scripts/run_iadsk.sh
```

### Verificar Instalación

```bash
./skills/dsk/scripts/run_iadsk.sh -- help
```

Debería mostrar la ayuda sin errores.

---

## Recursos

- **Repositorio iaDSK**: https://github.com/ABCronosMods/iaDSK
- **Documentación iaDSK**: https://github.com/ABCronosMods/iaDSK/tree/main/doc
- **Amstrad CPC Wiki**: https://www.cpcwiki.eu/

---

## Contribuir

¡Las contribuciones son bienvenidas! Si quieres añadir una nueva skill o mejorar una existente:

1. Haz fork de este repositorio
2. Crea un nuevo directorio de skill bajo `skills/`
3. Añade tu `SKILL.md` con el frontmatter YAML apropiado
4. Actualiza `.claude-plugin/marketplace.json` para incluir tu skill
5. Prueba localmente antes de enviar
6. Envía un pull request

Consulta la [especificación Agent Skills](https://agentskills.io) para directrices de creación de skills.

---

## Licencia

Licencia MIT - Ver [LICENSE](LICENSE) para más detalles.

---

*Parte de la organización [CPCReady](https://github.com/CPCReady)*

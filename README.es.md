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
npx skills add CPCReady/skills/dsk
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

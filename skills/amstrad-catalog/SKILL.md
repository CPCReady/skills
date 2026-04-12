---
name: amstrad-catalog
description: Indexa y consulta catálogos técnicos de imágenes Amstrad .dsk/.cdt/.tzx usando CATALOG_AMSTRAD, con base SQLite incremental por hash y consultas en lenguaje natural.
---

# amstrad-catalog

## Flujo recomendado

1. Validar la variable `CATALOG_AMSTRAD`.
   - Si falta o está vacía, abortar con: `Define/exporta CATALOG_AMSTRAD antes de ejecutar amstrad-catalog`.
2. Ejecutar `index` para primer escaneo o actualización incremental.
3. Ejecutar `query --question "..."` para consultas en lenguaje natural.
4. Ejecutar `stats` para estado global del catálogo.
5. Usar `reindex --full` solo cuando quieras reconstrucción completa.

## Ubicación de datos

- Base principal: `"$CATALOG_AMSTRAD/.amstrad-catalog/catalog.db"`
- El catálogo usa SQLite y conserva trazabilidad de archivos borrados (`status=DELETED`).

## Comandos

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py reindex --full
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "discos mayores de 700 KB"
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats
```

Formato de salida:
- Default: `--format json`
- Humano: `--format markdown`

Ejemplos:

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index --format markdown
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats --format markdown
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "cintas con turbo" --format markdown
```

## Cobertura técnica indexada

- Común: ruta absoluta, nombre, extensión, tamaño, `mtime`, `ctime`, `sha256`, estado, fecha de indexación.
- DSK:
  - Espacio total/usado/libre.
  - Catálogo de archivos (`name`, `user`, `load`, `exec`, `size`, atributos).
  - Cabecera técnica (`MV - CPCEMU` / `EXTENDED CPC`, tracks, sides, track size).
- CDT/TZX:
  - Versión de cinta, recuento de bloques, recuentos turbo/pure/normal/pause.
  - Headers lógicos (`filename`, `type`, `load_addr`, `start_addr`, `length`, first/last).

## Reglas operativas para agentes

- No recorrer rutas fuera de `CATALOG_AMSTRAD`.
- No detener el lote por una imagen corrupta: registrar `ERROR` y continuar.
- Para consultas, usar siempre `query --question` (sin SQL libre del usuario).
- Si no hay resultados en una consulta, devolver sugerencias de reformulación.

## Dependencias

- Python 3.8+ (stdlib only).
- Skill `dsk` disponible para lectura de `.dsk` (iaDSK).
- Skill `cdt` disponible para lectura de `.cdt/.tzx` (ia2cdt.py).

## Referencia

- Recetas: `references/cli-recipes.md`

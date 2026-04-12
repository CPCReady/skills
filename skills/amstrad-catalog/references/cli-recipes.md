# amstrad-catalog CLI Recipes

## Requisito obligatorio

Define la variable de entorno `CATALOG_AMSTRAD` apuntando al directorio raíz a indexar.

```bash
export CATALOG_AMSTRAD="/ruta/a/mi/catalogo-amstrad"
```

Si falta:

```text
Define/exporta CATALOG_AMSTRAD antes de ejecutar amstrad-catalog
```

## Indexación incremental

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index --format markdown
```

## Reindexación completa

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py reindex --full
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py reindex --full --format markdown
```

## Estadísticas

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats --format markdown
```

## Consultas en lenguaje natural

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "resumen"
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "discos mayores de 700 KB" --format markdown
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "cintas con turbo" --format markdown
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "duplicados" --format markdown
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "errores" --format markdown
```

## Esquema persistente

Base SQLite en:

```text
$CATALOG_AMSTRAD/.amstrad-catalog/catalog.db
```

Tablas principales:
- `images`
- `dsk_summary`
- `dsk_files`
- `cdt_summary`
- `cdt_files`
- `scan_runs`

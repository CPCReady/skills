# amstrad-catalog

Skill para catalogar y consultar colecciones de imágenes Amstrad (`.dsk`, `.cdt`, `.tzx`) bajo `CATALOG_AMSTRAD`.

## Puntos clave
- Variable obligatoria: `CATALOG_AMSTRAD`
- Backend: SQLite (`$CATALOG_AMSTRAD/.amstrad-catalog/catalog.db`)
- Indexación incremental por `size + mtime + sha256`
- Consultas en lenguaje natural con `query --question "..."`

## Comandos

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py reindex --full
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "cintas con turbo"
```

Añade `--format markdown` para salida legible.

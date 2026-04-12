# amstrad-catalog

Catalog and query Amstrad disk/tape image collections (`.dsk`, `.cdt`, `.tzx`) under `CATALOG_AMSTRAD`.

## Key points
- Mandatory env var: `CATALOG_AMSTRAD`
- Storage backend: SQLite (`$CATALOG_AMSTRAD/.amstrad-catalog/catalog.db`)
- Incremental indexing by `size + mtime + sha256`
- Natural language queries via `query --question "..."`

## Commands

```bash
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py index
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py reindex --full
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py stats
python3 skills/amstrad-catalog/scripts/amstrad_catalog.py query --question "tapes with turbo"
```

Add `--format markdown` for human-readable output.

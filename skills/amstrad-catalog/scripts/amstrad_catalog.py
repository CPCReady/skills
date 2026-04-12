#!/usr/bin/env python3
"""amstrad-catalog: index and query Amstrad .dsk/.cdt/.tzx collections."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CATALOG_ENV = "CATALOG_AMSTRAD"
CATALOG_DIRNAME = ".amstrad-catalog"
DB_FILENAME = "catalog.db"
VALID_EXTENSIONS = {".dsk", ".cdt", ".tzx"}
STATUS_ACTIVE = "ACTIVE"
STATUS_ERROR = "ERROR"
STATUS_DELETED = "DELETED"


class CatalogError(RuntimeError):
    """Controlled error for user-facing failures."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_path(path: Path) -> str:
    return str(path.resolve())


def to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text, 0)
    except ValueError:
        return None


def ensure_catalog_root() -> Tuple[Path, Path, Path]:
    root_var = os.getenv(CATALOG_ENV, "").strip()
    if not root_var:
        raise CatalogError("Define/exporta CATALOG_AMSTRAD antes de ejecutar amstrad-catalog")

    root = Path(root_var).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise CatalogError(f"{CATALOG_ENV} no apunta a un directorio válido: {root}")

    catalog_dir = root / CATALOG_DIRNAME
    catalog_dir.mkdir(parents=True, exist_ok=True)

    return root, catalog_dir, catalog_dir / DB_FILENAME


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            ext TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            mtime REAL NOT NULL,
            ctime REAL,
            sha256 TEXT,
            status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'ERROR', 'DELETED')),
            error_msg TEXT,
            indexed_at TEXT NOT NULL,
            format_kind TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_images_status ON images(status);
        CREATE INDEX IF NOT EXISTS idx_images_ext ON images(ext);
        CREATE INDEX IF NOT EXISTS idx_images_sha ON images(sha256);

        CREATE TABLE IF NOT EXISTS dsk_summary (
            image_id INTEGER PRIMARY KEY,
            format_name TEXT,
            tracks INTEGER,
            sides INTEGER,
            track_size_bytes INTEGER,
            total_kb INTEGER,
            used_kb INTEGER,
            free_kb INTEGER,
            files_count INTEGER,
            FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS dsk_files (
            id INTEGER PRIMARY KEY,
            image_id INTEGER NOT NULL,
            name TEXT,
            user_num INTEGER,
            load_addr INTEGER,
            exec_addr INTEGER,
            size_bytes INTEGER,
            size_kb INTEGER,
            read_only INTEGER,
            system_file INTEGER,
            FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_dsk_files_image ON dsk_files(image_id);

        CREATE TABLE IF NOT EXISTS cdt_summary (
            image_id INTEGER PRIMARY KEY,
            version TEXT,
            blocks_count INTEGER,
            turbo_blocks INTEGER,
            pure_blocks INTEGER,
            normal_blocks INTEGER,
            pause_blocks INTEGER,
            FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cdt_files (
            id INTEGER PRIMARY KEY,
            image_id INTEGER NOT NULL,
            filename TEXT,
            file_type TEXT,
            load_addr INTEGER,
            start_addr INTEGER,
            length INTEGER,
            first_block INTEGER,
            last_block INTEGER,
            FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_cdt_files_image ON cdt_files(image_id);

        CREATE TABLE IF NOT EXISTS scan_runs (
            id INTEGER PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            mode TEXT NOT NULL,
            scanned INTEGER NOT NULL,
            indexed INTEGER NOT NULL,
            updated INTEGER NOT NULL,
            unchanged INTEGER NOT NULL,
            errors INTEGER NOT NULL
        );
        """
    )


@dataclass
class Toolchain:
    repo_root: Path
    iadsk_binary: Optional[Path]
    cdt_script: Path
    python_bin: str


@dataclass
class DskHeader:
    format_name: str
    tracks: int
    sides: int
    track_size_bytes: Optional[int]


def detect_repo_root(script_path: Path) -> Path:
    # .../skills/amstrad-catalog/scripts/amstrad_catalog.py -> repo root
    return script_path.resolve().parents[3]


def platform_key() -> str:
    sys_name = platform.system().lower()
    if sys_name == "darwin":
        return "macos"
    if sys_name.startswith("msys") or sys_name.startswith("mingw") or sys_name == "windows":
        return "windows"
    return "linux"


def arch_key() -> str:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine


def resolve_iadsk_binary(repo_root: Path) -> Optional[Path]:
    explicit = os.getenv("IADSK_BINARY", "").strip()
    if explicit:
        path = Path(explicit).expanduser()
        if path.exists():
            return path.resolve()

    from_path = shutil_which("iaDSK")
    if from_path is not None:
        return from_path

    home = Path.home()
    default_bin = home / "bin" / ("iaDSK.exe" if platform_key() == "windows" else "iaDSK")
    if default_bin.exists():
        return default_bin.resolve()

    bundled = repo_root / "skills" / "dsk" / "assets" / "bin" / f"{platform_key()}-{arch_key()}"
    bundled = bundled / ("iaDSK.exe" if platform_key() == "windows" else "iaDSK")
    if bundled.exists():
        return bundled.resolve()

    return None


def shutil_which(binary: str) -> Optional[Path]:
    candidate = None
    try:
        from shutil import which

        candidate = which(binary)
    except Exception:
        candidate = None

    return Path(candidate).resolve() if candidate else None


def resolve_toolchain() -> Toolchain:
    script_path = Path(__file__)
    repo_root = detect_repo_root(script_path)
    iadsk_binary = resolve_iadsk_binary(repo_root)

    cdt_script = repo_root / "skills" / "cdt" / "scripts" / "ia2cdt.py"
    if not cdt_script.exists():
        raise CatalogError(f"No se encontró ia2cdt.py en {cdt_script}")

    return Toolchain(
        repo_root=repo_root,
        iadsk_binary=iadsk_binary,
        cdt_script=cdt_script,
        python_bin=sys.executable or "python3",
    )


def run_cmd(args: Sequence[str], timeout: int = 120) -> str:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        details = stderr or stdout or "sin salida"
        raise CatalogError(f"Comando falló ({proc.returncode}): {' '.join(args)} -> {details}")
    output = (proc.stdout or "").strip()
    if not output:
        raise CatalogError(f"Comando sin salida JSON: {' '.join(args)}")
    return output


def parse_json_output(raw: str, command: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        snippet = raw[:250].replace("\n", " ")
        raise CatalogError(f"Salida JSON inválida en {command}: {exc}. Snippet: {snippet}") from exc

    if not isinstance(payload, dict):
        raise CatalogError(f"Salida inesperada en {command}: se esperaba objeto JSON")
    return payload


def read_dsk_header(path: Path) -> DskHeader:
    header = path.read_bytes()[:256]
    if len(header) < 256:
        raise CatalogError(f"DSK demasiado pequeño para cabecera válida: {path}")

    if header.startswith(b"MV - CPCEMU Disk-File"):
        format_name = "MV - CPCEMU"
    elif header.startswith(b"EXTENDED CPC DSK File"):
        format_name = "EXTENDED CPC"
    else:
        format_name = "UNKNOWN"

    tracks = int(header[0x30])
    sides = int(header[0x31])
    track_size_bytes: Optional[int] = None

    if format_name == "MV - CPCEMU":
        track_size_bytes = int.from_bytes(header[0x32:0x34], byteorder="little", signed=False)
    elif format_name == "EXTENDED CPC":
        count = tracks * sides
        raw_sizes = header[0x34 : 0x34 + count]
        sizes = [int(v) * 256 for v in raw_sizes if int(v) > 0]
        if sizes:
            track_size_bytes = max(sizes)

    return DskHeader(format_name=format_name, tracks=tracks, sides=sides, track_size_bytes=track_size_bytes)


def run_iadsk_cat_free(toolchain: Toolchain, dsk_file: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if toolchain.iadsk_binary is None:
        raise CatalogError("iaDSK no disponible. Instala la skill dsk o define IADSK_BINARY.")

    cat_raw = run_cmd([str(toolchain.iadsk_binary), "cat", "--dsk", str(dsk_file)])
    free_raw = run_cmd([str(toolchain.iadsk_binary), "free", "--dsk", str(dsk_file)])

    cat_payload = parse_json_output(cat_raw, "iaDSK cat")
    free_payload = parse_json_output(free_raw, "iaDSK free")

    if not cat_payload.get("ok", False):
        msg = extract_error_message(cat_payload)
        raise CatalogError(f"iaDSK cat error: {msg}")
    if not free_payload.get("ok", False):
        msg = extract_error_message(free_payload)
        raise CatalogError(f"iaDSK free error: {msg}")

    return cat_payload.get("data", {}), free_payload.get("data", {})


def run_ia2cdt_cat(toolchain: Toolchain, tape_file: Path) -> Dict[str, Any]:
    args = [toolchain.python_bin, str(toolchain.cdt_script), "cat", str(tape_file)]
    raw = run_cmd(args)
    payload = parse_json_output(raw, "ia2cdt cat")
    if "blocks" not in payload:
        raise CatalogError("ia2cdt cat devolvió JSON sin 'blocks'")
    return payload


def extract_error_message(payload: Dict[str, Any]) -> str:
    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        first = errors[0]
        if isinstance(first, dict):
            return str(first.get("message") or first.get("code") or first)
        return str(first)
    return "error desconocido"


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def discover_images(root: Path) -> List[Path]:
    discovered: List[Path] = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != CATALOG_DIRNAME]
        for filename in files:
            path = Path(current_root) / filename
            if path.suffix.lower() in VALID_EXTENSIONS:
                discovered.append(path.resolve())
    discovered.sort()
    return discovered


def fetch_existing_images(conn: sqlite3.Connection) -> Dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT id, path, size_bytes, mtime, sha256, status
        FROM images
        """
    ).fetchall()
    return {str(row["path"]): row for row in rows}


def upsert_image(
    conn: sqlite3.Connection,
    *,
    image_id: Optional[int],
    path: str,
    name: str,
    ext: str,
    size_bytes: int,
    mtime: float,
    ctime: Optional[float],
    sha256: Optional[str],
    status: str,
    error_msg: Optional[str],
    indexed_at: str,
    format_kind: str,
) -> int:
    if image_id is None:
        cur = conn.execute(
            """
            INSERT INTO images(
                path, name, ext, size_bytes, mtime, ctime,
                sha256, status, error_msg, indexed_at, format_kind
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                path,
                name,
                ext,
                size_bytes,
                mtime,
                ctime,
                sha256,
                status,
                error_msg,
                indexed_at,
                format_kind,
            ),
        )
        return int(cur.lastrowid)

    conn.execute(
        """
        UPDATE images
        SET
            path = ?,
            name = ?,
            ext = ?,
            size_bytes = ?,
            mtime = ?,
            ctime = ?,
            sha256 = ?,
            status = ?,
            error_msg = ?,
            indexed_at = ?,
            format_kind = ?
        WHERE id = ?
        """,
        (
            path,
            name,
            ext,
            size_bytes,
            mtime,
            ctime,
            sha256,
            status,
            error_msg,
            indexed_at,
            format_kind,
            image_id,
        ),
    )
    return image_id


def clear_technical_rows(conn: sqlite3.Connection, image_id: int) -> None:
    conn.execute("DELETE FROM dsk_summary WHERE image_id = ?", (image_id,))
    conn.execute("DELETE FROM dsk_files WHERE image_id = ?", (image_id,))
    conn.execute("DELETE FROM cdt_summary WHERE image_id = ?", (image_id,))
    conn.execute("DELETE FROM cdt_files WHERE image_id = ?", (image_id,))


def save_dsk_technical(conn: sqlite3.Connection, image_id: int, cat_data: Dict[str, Any], free_data: Dict[str, Any], header: DskHeader) -> None:
    entries = cat_data.get("entries")
    if not isinstance(entries, list):
        entries = []

    total_kb = to_int(free_data.get("total_kb"))
    used_kb = to_int(free_data.get("used_kb"))
    free_kb = to_int(free_data.get("free_kb"))

    conn.execute(
        """
        INSERT INTO dsk_summary(
            image_id, format_name, tracks, sides, track_size_bytes,
            total_kb, used_kb, free_kb, files_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(image_id) DO UPDATE SET
            format_name = excluded.format_name,
            tracks = excluded.tracks,
            sides = excluded.sides,
            track_size_bytes = excluded.track_size_bytes,
            total_kb = excluded.total_kb,
            used_kb = excluded.used_kb,
            free_kb = excluded.free_kb,
            files_count = excluded.files_count
        """,
        (
            image_id,
            header.format_name,
            header.tracks,
            header.sides,
            header.track_size_bytes,
            total_kb,
            used_kb,
            free_kb,
            len(entries),
        ),
    )

    conn.executemany(
        """
        INSERT INTO dsk_files(
            image_id, name, user_num, load_addr, exec_addr,
            size_bytes, size_kb, read_only, system_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                image_id,
                str(entry.get("name", "")),
                to_int(entry.get("user")),
                to_int(entry.get("load")),
                to_int(entry.get("exec")),
                to_int(entry.get("size_bytes")),
                to_int(entry.get("size_kb")),
                1 if bool(entry.get("read_only")) else 0,
                1 if bool(entry.get("system")) else 0,
            )
            for entry in entries
            if isinstance(entry, dict)
        ],
    )


def count_block_types(blocks: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    turbo = 0
    pure = 0
    normal = 0
    pause = 0
    for block in blocks:
        block_type = str(block.get("type", "")).lower()
        if "turbo" in block_type:
            turbo += 1
        elif "pure" in block_type:
            pure += 1
        elif "normal" in block_type:
            normal += 1
        elif "pause" in block_type:
            pause += 1
    return {
        "turbo": turbo,
        "pure": pure,
        "normal": normal,
        "pause": pause,
    }


def save_tape_technical(conn: sqlite3.Connection, image_id: int, payload: Dict[str, Any]) -> None:
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        blocks = []

    counters = count_block_types([b for b in blocks if isinstance(b, dict)])

    conn.execute(
        """
        INSERT INTO cdt_summary(
            image_id, version, blocks_count, turbo_blocks,
            pure_blocks, normal_blocks, pause_blocks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(image_id) DO UPDATE SET
            version = excluded.version,
            blocks_count = excluded.blocks_count,
            turbo_blocks = excluded.turbo_blocks,
            pure_blocks = excluded.pure_blocks,
            normal_blocks = excluded.normal_blocks,
            pause_blocks = excluded.pause_blocks
        """,
        (
            image_id,
            str(payload.get("version", "")),
            len(blocks),
            counters["turbo"],
            counters["pure"],
            counters["normal"],
            counters["pause"],
        ),
    )

    records: List[Tuple[Any, ...]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        header = block.get("header")
        if not isinstance(header, dict):
            continue
        records.append(
            (
                image_id,
                str(header.get("filename", "")),
                str(header.get("type", "")),
                to_int(header.get("load_addr")),
                to_int(header.get("start_addr")),
                to_int(header.get("length")),
                1 if bool(header.get("first_block")) else 0,
                1 if bool(header.get("last_block")) else 0,
            )
        )

    if records:
        conn.executemany(
            """
            INSERT INTO cdt_files(
                image_id, filename, file_type, load_addr,
                start_addr, length, first_block, last_block
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )


def record_scan_run(
    conn: sqlite3.Connection,
    *,
    started_at: str,
    ended_at: str,
    mode: str,
    scanned: int,
    indexed: int,
    updated: int,
    unchanged: int,
    errors: int,
) -> None:
    conn.execute(
        """
        INSERT INTO scan_runs(
            started_at, ended_at, mode, scanned, indexed,
            updated, unchanged, errors
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (started_at, ended_at, mode, scanned, indexed, updated, unchanged, errors),
    )


def mark_deleted_images(conn: sqlite3.Connection, seen_paths: set[str], existing: Dict[str, sqlite3.Row], now_iso: str) -> int:
    deleted = 0
    for path, row in existing.items():
        if path in seen_paths:
            continue
        if row["status"] == STATUS_DELETED:
            continue
        conn.execute(
            "UPDATE images SET status = ?, error_msg = NULL, indexed_at = ? WHERE id = ?",
            (STATUS_DELETED, now_iso, int(row["id"])),
        )
        deleted += 1
    return deleted


def run_index(toolchain: Toolchain, conn: sqlite3.Connection, root: Path, mode: str, full_reindex: bool) -> Dict[str, Any]:
    started_at = utc_now()
    discovered = discover_images(root)
    existing = fetch_existing_images(conn)

    scanned = len(discovered)
    indexed = 0
    updated = 0
    unchanged = 0
    errors = 0

    seen_paths: set[str] = set()

    for image in discovered:
        path_text = normalize_path(image)
        seen_paths.add(path_text)

        stat = image.stat()
        size_bytes = int(stat.st_size)
        mtime = float(stat.st_mtime)
        ctime = float(getattr(stat, "st_ctime", stat.st_mtime))
        ext = image.suffix.lower()
        format_kind = "dsk" if ext == ".dsk" else "tape"

        row = existing.get(path_text)
        row_id = int(row["id"]) if row else None

        if row and not full_reindex:
            same_size = int(row["size_bytes"]) == size_bytes
            same_mtime = abs(float(row["mtime"]) - mtime) < 1e-6
            if same_size and same_mtime and row["status"] == STATUS_ACTIVE:
                unchanged += 1
                continue

        sha256 = compute_sha256(image)

        if row and not full_reindex and row["sha256"] == sha256 and row["status"] == STATUS_ACTIVE:
            upsert_image(
                conn,
                image_id=row_id,
                path=path_text,
                name=image.name,
                ext=ext,
                size_bytes=size_bytes,
                mtime=mtime,
                ctime=ctime,
                sha256=sha256,
                status=STATUS_ACTIVE,
                error_msg=None,
                indexed_at=utc_now(),
                format_kind=format_kind,
            )
            unchanged += 1
            continue

        clear_technical_rows = row is not None
        if clear_technical_rows and row_id is not None:
            clear_technical_rows_fn(conn, row_id)

        image_status = STATUS_ACTIVE
        error_msg: Optional[str] = None

        try:
            if ext == ".dsk":
                cat_data, free_data = run_iadsk_cat_free(toolchain, image)
                dsk_header = read_dsk_header(image)
            else:
                cat_payload = run_ia2cdt_cat(toolchain, image)
        except Exception as exc:
            image_status = STATUS_ERROR
            error_msg = str(exc)
            errors += 1

        image_id = upsert_image(
            conn,
            image_id=row_id,
            path=path_text,
            name=image.name,
            ext=ext,
            size_bytes=size_bytes,
            mtime=mtime,
            ctime=ctime,
            sha256=sha256,
            status=image_status,
            error_msg=error_msg,
            indexed_at=utc_now(),
            format_kind=format_kind,
        )

        if image_status == STATUS_ACTIVE:
            try:
                if ext == ".dsk":
                    save_dsk_technical(conn, image_id, cat_data, free_data, dsk_header)
                else:
                    save_tape_technical(conn, image_id, cat_payload)
            except Exception as exc:
                # Persist parser failures as image errors but keep run alive.
                errors += 1
                clear_technical_rows_fn(conn, image_id)
                conn.execute(
                    "UPDATE images SET status = ?, error_msg = ?, indexed_at = ? WHERE id = ?",
                    (STATUS_ERROR, str(exc), utc_now(), image_id),
                )
                image_status = STATUS_ERROR

        if row is None:
            indexed += 1
        elif image_status == STATUS_ACTIVE:
            updated += 1

    deleted = mark_deleted_images(conn, seen_paths, existing, utc_now())
    ended_at = utc_now()

    record_scan_run(
        conn,
        started_at=started_at,
        ended_at=ended_at,
        mode=mode,
        scanned=scanned,
        indexed=indexed,
        updated=updated,
        unchanged=unchanged,
        errors=errors,
    )

    return {
        "catalog_root": normalize_path(root),
        "db_path": normalize_path(Path(conn.execute("PRAGMA database_list").fetchone()[2])),
        "mode": mode,
        "scanned": scanned,
        "indexed": indexed,
        "updated": updated,
        "unchanged": unchanged,
        "errors": errors,
        "deleted_marked": deleted,
        "started_at": started_at,
        "ended_at": ended_at,
    }


def clear_technical_rows_fn(conn: sqlite3.Connection, image_id: int) -> None:
    clear_technical_rows(conn, image_id)


def get_stats(conn: sqlite3.Connection, root: Path, db_path: Path) -> Dict[str, Any]:
    totals = conn.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) AS errors,
            SUM(CASE WHEN status = 'DELETED' THEN 1 ELSE 0 END) AS deleted
        FROM images
        """
    ).fetchone()

    by_ext_rows = conn.execute(
        """
        SELECT ext, COUNT(*) AS count
        FROM images
        GROUP BY ext
        ORDER BY ext
        """
    ).fetchall()

    last_run = conn.execute(
        """
        SELECT started_at, ended_at, mode, scanned, indexed, updated, unchanged, errors
        FROM scan_runs
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    return {
        "catalog_root": normalize_path(root),
        "db_path": normalize_path(db_path),
        "images": {
            "total": int(totals["total"] or 0),
            "active": int(totals["active"] or 0),
            "errors": int(totals["errors"] or 0),
            "deleted": int(totals["deleted"] or 0),
        },
        "by_extension": [{"ext": str(r["ext"]), "count": int(r["count"])} for r in by_ext_rows],
        "last_scan": dict(last_run) if last_run is not None else None,
    }


def extract_size_threshold(question: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*(gb|g|mb|m|kb|k|bytes|byte|b)", question, flags=re.IGNORECASE)
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2).lower()
    if unit in {"gb", "g"}:
        return value * 1024 * 1024 * 1024
    if unit in {"mb", "m"}:
        return value * 1024 * 1024
    if unit in {"kb", "k"}:
        return value * 1024
    return value


def detect_intent(question: str) -> Tuple[str, Dict[str, Any]]:
    q = question.strip().lower()

    if any(token in q for token in ("resumen", "summary", "estado", "stats", "estadisticas", "estadísticas")):
        return "summary", {}

    if any(token in q for token in ("duplic", "repetid", "same hash", "mismo hash")):
        return "duplicates", {}

    if any(token in q for token in ("corrupt", "error", "inválid", "invalid")):
        return "errors", {}

    if any(token in q for token in ("turbo", "bloque turbo")):
        return "turbo_tapes", {}

    size_threshold = extract_size_threshold(q)
    if size_threshold is not None and any(
        token in q
        for token in (
            "mayor",
            "mayores",
            "mas de",
            "más de",
            "greater",
            "over",
            "at least",
            "bigger",
            "larger",
        )
    ):
        only_dsk = any(token in q for token in ("dsk", "disco", "disk"))
        only_tape = any(token in q for token in ("cinta", "tape", "cdt", "tzx"))
        return "size_filter", {"min_bytes": size_threshold, "only_dsk": only_dsk, "only_tape": only_tape}

    return "text_search", {"query": question.strip()}


def query_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status='ACTIVE' THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN status='ERROR' THEN 1 ELSE 0 END) AS errors,
            SUM(CASE WHEN status='DELETED' THEN 1 ELSE 0 END) AS deleted,
            SUM(CASE WHEN ext='.dsk' AND status='ACTIVE' THEN 1 ELSE 0 END) AS active_dsk,
            SUM(CASE WHEN ext IN ('.cdt', '.tzx') AND status='ACTIVE' THEN 1 ELSE 0 END) AS active_tape
        FROM images
        """
    ).fetchone()
    return {
        "total_images": int(row["total"] or 0),
        "active": int(row["active"] or 0),
        "errors": int(row["errors"] or 0),
        "deleted": int(row["deleted"] or 0),
        "active_dsk": int(row["active_dsk"] or 0),
        "active_tape": int(row["active_tape"] or 0),
    }


def query_duplicates(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT sha256, COUNT(*) AS copies, GROUP_CONCAT(path, '\n') AS paths
        FROM images
        WHERE status='ACTIVE' AND sha256 IS NOT NULL AND sha256 != ''
        GROUP BY sha256
        HAVING COUNT(*) > 1
        ORDER BY copies DESC, sha256 ASC
        """
    ).fetchall()

    result: List[Dict[str, Any]] = []
    for row in rows:
        result.append(
            {
                "sha256": row["sha256"],
                "copies": int(row["copies"]),
                "paths": str(row["paths"]).split("\n"),
            }
        )
    return result


def query_errors(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT path, ext, error_msg, indexed_at
        FROM images
        WHERE status='ERROR'
        ORDER BY indexed_at DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def query_turbo_tapes(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT i.path, i.name, i.ext, c.version, c.blocks_count, c.turbo_blocks
        FROM images i
        JOIN cdt_summary c ON c.image_id = i.id
        WHERE i.status='ACTIVE' AND i.ext IN ('.cdt', '.tzx') AND c.turbo_blocks > 0
        ORDER BY c.turbo_blocks DESC, i.name ASC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def query_by_size(conn: sqlite3.Connection, min_bytes: int, only_dsk: bool, only_tape: bool) -> List[Dict[str, Any]]:
    where = ["status='ACTIVE'", "size_bytes >= ?"]
    params: List[Any] = [int(min_bytes)]

    if only_dsk and not only_tape:
        where.append("ext = '.dsk'")
    elif only_tape and not only_dsk:
        where.append("ext IN ('.cdt', '.tzx')")

    sql = f"""
        SELECT path, name, ext, size_bytes
        FROM images
        WHERE {' AND '.join(where)}
        ORDER BY size_bytes DESC
        LIMIT 200
    """
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def tokenize_query(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z0-9_\-\.]+", text)
    return [tok for tok in tokens if len(tok) >= 3][:6]


def query_text_search(conn: sqlite3.Connection, text: str) -> List[Dict[str, Any]]:
    tokens = tokenize_query(text)
    if not tokens:
        return []

    clauses = []
    params: List[str] = []
    for tok in tokens:
        clauses.append("(name LIKE ? OR path LIKE ?)")
        term = f"%{tok}%"
        params.extend([term, term])

    sql = f"""
        SELECT path, name, ext, size_bytes, status
        FROM images
        WHERE {' OR '.join(clauses)}
        ORDER BY
            CASE status
                WHEN 'ACTIVE' THEN 0
                WHEN 'ERROR' THEN 1
                ELSE 2
            END,
            size_bytes DESC,
            name ASC
        LIMIT 200
    """

    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def run_nl_query(conn: sqlite3.Connection, question: str) -> Dict[str, Any]:
    intent, params = detect_intent(question)

    if intent == "summary":
        return {
            "intent": intent,
            "question": question,
            "result": query_summary(conn),
        }

    if intent == "duplicates":
        return {
            "intent": intent,
            "question": question,
            "rows": query_duplicates(conn),
        }

    if intent == "errors":
        return {
            "intent": intent,
            "question": question,
            "rows": query_errors(conn),
        }

    if intent == "turbo_tapes":
        return {
            "intent": intent,
            "question": question,
            "rows": query_turbo_tapes(conn),
        }

    if intent == "size_filter":
        rows = query_by_size(
            conn,
            min_bytes=int(params["min_bytes"]),
            only_dsk=bool(params["only_dsk"]),
            only_tape=bool(params["only_tape"]),
        )
        return {
            "intent": intent,
            "question": question,
            "min_bytes": int(params["min_bytes"]),
            "rows": rows,
        }

    rows = query_text_search(conn, params.get("query", question))
    return {
        "intent": "text_search",
        "question": question,
        "rows": rows,
    }


def bytes_human(value: Optional[int]) -> str:
    if value is None:
        return ""
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{int(value)} B"


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", "<br>")
    return text.replace("|", "\\|")


def markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(col) for col in row) + " |")
    return "\n".join(lines)


def render_index_markdown(data: Dict[str, Any]) -> str:
    rows = [
        ["Root", data.get("catalog_root", "")],
        ["DB", data.get("db_path", "")],
        ["Mode", data.get("mode", "")],
        ["Scanned", data.get("scanned", 0)],
        ["Indexed", data.get("indexed", 0)],
        ["Updated", data.get("updated", 0)],
        ["Unchanged", data.get("unchanged", 0)],
        ["Errors", data.get("errors", 0)],
        ["Deleted Marked", data.get("deleted_marked", 0)],
        ["Started", data.get("started_at", "")],
        ["Ended", data.get("ended_at", "")],
    ]
    return "## Index Result\n\n" + markdown_table(["Field", "Value"], rows)


def render_stats_markdown(data: Dict[str, Any]) -> str:
    output: List[str] = []
    output.append("## Catalog Stats")
    output.append("")

    output.append(markdown_table(
        ["Field", "Value"],
        [
            ["Catalog Root", data.get("catalog_root", "")],
            ["DB", data.get("db_path", "")],
            ["Total Images", data["images"].get("total", 0)],
            ["Active", data["images"].get("active", 0)],
            ["Errors", data["images"].get("errors", 0)],
            ["Deleted", data["images"].get("deleted", 0)],
        ],
    ))

    by_ext = data.get("by_extension", [])
    if by_ext:
        output.append("")
        output.append("### By Extension")
        output.append(markdown_table(["Extension", "Count"], [[row["ext"], row["count"]] for row in by_ext]))

    last_scan = data.get("last_scan")
    if last_scan:
        output.append("")
        output.append("### Last Scan")
        output.append(markdown_table(
            ["Field", "Value"],
            [
                ["Mode", last_scan.get("mode", "")],
                ["Started", last_scan.get("started_at", "")],
                ["Ended", last_scan.get("ended_at", "")],
                ["Scanned", last_scan.get("scanned", 0)],
                ["Indexed", last_scan.get("indexed", 0)],
                ["Updated", last_scan.get("updated", 0)],
                ["Unchanged", last_scan.get("unchanged", 0)],
                ["Errors", last_scan.get("errors", 0)],
            ],
        ))

    return "\n".join(output)


def render_query_markdown(data: Dict[str, Any]) -> str:
    intent = data.get("intent")
    output: List[str] = []

    output.append("## Query")
    output.append("")
    output.append(f"- Question: `{data.get('question', '')}`")
    output.append(f"- Intent: `{intent}`")

    if intent == "summary":
        summary = data.get("result", {})
        output.append("")
        output.append(markdown_table(
            ["Metric", "Value"],
            [[key, value] for key, value in summary.items()],
        ))
        return "\n".join(output)

    rows = data.get("rows", [])
    if not rows:
        output.append("")
        output.append("No results.")
        output.append("")
        output.append("Try a different query, for example: `duplicados`, `errores`, `cintas con turbo`, `discos mayores de 700 KB`.")
        return "\n".join(output)

    output.append("")

    if intent == "duplicates":
        table_rows: List[List[Any]] = []
        for row in rows:
            table_rows.append([row.get("sha256", ""), row.get("copies", 0), "<br>".join(row.get("paths", []))])
        output.append(markdown_table(["SHA256", "Copies", "Paths"], table_rows))
        return "\n".join(output)

    if intent == "errors":
        output.append(markdown_table(
            ["Path", "Ext", "Error", "Indexed At"],
            [[r.get("path", ""), r.get("ext", ""), r.get("error_msg", ""), r.get("indexed_at", "")] for r in rows],
        ))
        return "\n".join(output)

    if intent == "turbo_tapes":
        output.append(markdown_table(
            ["Name", "Ext", "Turbo Blocks", "Total Blocks", "Version", "Path"],
            [
                [
                    r.get("name", ""),
                    r.get("ext", ""),
                    r.get("turbo_blocks", 0),
                    r.get("blocks_count", 0),
                    r.get("version", ""),
                    r.get("path", ""),
                ]
                for r in rows
            ],
        ))
        return "\n".join(output)

    if intent == "size_filter":
        output.append(markdown_table(
            ["Name", "Ext", "Size", "Path"],
            [[r.get("name", ""), r.get("ext", ""), bytes_human(to_int(r.get("size_bytes"))), r.get("path", "")] for r in rows],
        ))
        return "\n".join(output)

    output.append(markdown_table(
        ["Name", "Ext", "Status", "Size", "Path"],
        [
            [
                r.get("name", ""),
                r.get("ext", ""),
                r.get("status", ""),
                bytes_human(to_int(r.get("size_bytes"))),
                r.get("path", ""),
            ]
            for r in rows
        ],
    ))
    return "\n".join(output)


def response_envelope(command: str, data: Dict[str, Any], ok: bool = True, errors: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "ok": ok,
        "command": command,
        "data": data,
        "errors": errors or [],
        "meta": {
            "program": "amstrad-catalog",
            "schema": "1.0",
            "timestamp": utc_now(),
        },
    }


def print_response(command: str, data: Dict[str, Any], output_format: str) -> None:
    if output_format == "markdown":
        if command in {"index", "reindex"}:
            print(render_index_markdown(data))
            return
        if command == "stats":
            print(render_stats_markdown(data))
            return
        if command == "query":
            print(render_query_markdown(data))
            return

    print(json.dumps(response_envelope(command, data), indent=2, ensure_ascii=False))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="amstrad_catalog.py",
        description="Index and query Amstrad DSK/CDT/TZX collections.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Run incremental indexing")
    p_index.add_argument("--format", choices=["json", "markdown"], default="json")

    p_reindex = sub.add_parser("reindex", help="Run full reindex")
    p_reindex.add_argument("--full", action="store_true", help="Compatibility flag (full reindex always enabled)")
    p_reindex.add_argument("--format", choices=["json", "markdown"], default="json")

    p_stats = sub.add_parser("stats", help="Show catalog statistics")
    p_stats.add_argument("--format", choices=["json", "markdown"], default="json")

    p_query = sub.add_parser("query", help="Natural language query")
    p_query.add_argument("--question", required=True, help="Natural language question")
    p_query.add_argument("--format", choices=["json", "markdown"], default="json")

    return parser.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    root, _catalog_dir, db_path = ensure_catalog_root()
    toolchain = resolve_toolchain()

    with open_db(db_path) as conn:
        if args.command == "index":
            data = run_index(toolchain, conn, root, mode="incremental", full_reindex=False)
            conn.commit()
            print_response("index", data, args.format)
            return 0

        if args.command == "reindex":
            data = run_index(toolchain, conn, root, mode="full", full_reindex=True)
            conn.commit()
            print_response("reindex", data, args.format)
            return 0

        if args.command == "stats":
            data = get_stats(conn, root, db_path)
            print_response("stats", data, args.format)
            return 0

        if args.command == "query":
            data = run_nl_query(conn, args.question)
            print_response("query", data, args.format)
            return 0

    raise CatalogError(f"Comando no soportado: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CatalogError as exc:
        payload = response_envelope("error", {"message": str(exc)}, ok=False, errors=[str(exc)])
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        raise SystemExit(130)

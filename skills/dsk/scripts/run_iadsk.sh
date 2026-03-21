#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

binary=""
output_format="markdown"
args=()

while [[ $# -gt 0 ]]; do
	case "$1" in
	--binary)
		shift
		if [[ $# -eq 0 ]]; then
			echo "Missing value for --binary" >&2
			exit 1
		fi
		binary="$1"
		;;
	--raw-json)
		output_format="json"
		;;
	--format)
		shift
		if [[ $# -eq 0 ]]; then
			echo "Missing value for --format" >&2
			exit 1
		fi
		output_format="$1"
		;;
	--)
		shift
		args=("$@")
		break
		;;
	-h | --help)
		cat <<'USAGE'
Usage: run_iadsk.sh [--binary <path>] [--format markdown|json] [--raw-json] -- <iadsk args>
USAGE
		exit 0
		;;
	*)
		args+=("$1")
		;;
	esac
	shift
done

if [[ "$output_format" != "markdown" && "$output_format" != "json" ]]; then
	echo "Invalid --format value: $output_format (expected: markdown or json)" >&2
	exit 1
fi

if [[ ${#args[@]} -eq 0 ]]; then
	args=(help)
fi

resolve_platform() {
	local uname_s uname_m
	uname_s="$(uname -s)"
	uname_m="$(uname -m)"

	case "$uname_s" in
	Darwin) platform="macos" ;;
	Linux) platform="linux" ;;
	MINGW* | MSYS* | CYGWIN*) platform="windows" ;;
	*) platform="${uname_s,,}" ;;
	esac

	case "$uname_m" in
	x86_64 | amd64) arch="x64" ;;
	arm64 | aarch64) arch="arm64" ;;
	*) arch="${uname_m,,}" ;;
	esac
}

resolve_binary() {
	local platform arch
	resolve_platform

	if [[ -n "$binary" ]]; then
		if [[ -f "$binary" ]]; then
			echo "$binary"
			return 0
		fi
		echo "Binary not found: $binary" >&2
		return 1
	fi

	if command -v iaDSK >/dev/null 2>&1; then
		command -v iaDSK
		return 0
	fi

	local default_bin
	if [[ "$platform" == "windows" ]]; then
		default_bin="${USERPROFILE:-$HOME}/bin/iaDSK.exe"
	else
		default_bin="$HOME/.local/bin/iaDSK"
	fi
	if [[ -f "$default_bin" ]]; then
		echo "$default_bin"
		return 0
	fi

	local bundled="$SKILL_ROOT/assets/bin/${platform}-${arch}/iaDSK"
	if [[ "$platform" == "windows" ]]; then
		bundled="$SKILL_ROOT/assets/bin/${platform}-${arch}/iaDSK.exe"
	fi

	if [[ -f "$bundled" ]]; then
		if [[ "$platform" != "windows" ]]; then
			chmod +x "$bundled"
		fi
		echo "$bundled"
		return 0
	fi

	echo "iaDSK no está disponible para ${platform}-${arch}. Ejecuta primero scripts/install_iadsk.sh o install_iadsk.ps1." >&2
	return 1
}

render_markdown() {
	local json_file="$1"

	if ! command -v python3 >/dev/null 2>&1; then
		return 1
	fi

	python3 - "$json_file" <<'PY'
import json
import sys
from pathlib import Path


def value_to_text(value):
    if isinstance(value, bool):
        return "si" if value else "no"
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def md_escape(value):
    text = value_to_text(value)
    text = text.replace("\r\n", "<br>")
    text = text.replace("\n", "<br>")
    text = text.replace("|", "\\|")
    return text


def print_table(headers, rows):
    if not rows:
        return
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        print("| " + " | ".join(md_escape(cell) for cell in row) + " |")
    print()


def show_key_values(title, mapping, preferred=None):
    print(f"### {title}")
    keys = []
    if preferred:
        keys.extend([k for k in preferred if k in mapping])
    keys.extend([k for k in mapping.keys() if k not in keys])
    rows = [(k, mapping.get(k)) for k in keys]
    print_table(["Field", "Value"], rows)


def format_kb_value(value):
    """Format a numeric value with KB suffix"""
    if value == "" or value is None:
        return ""
    return f"{value} KB"


def format_cat(data):
    print("### Catalog")
    print(f"- Disk: `{md_escape(data.get('dsk', ''))}`")
    entries = data.get("entries", []) or []
    if entries:
        rows = []
        for entry in entries:
            attrs = ""
            if entry.get("read_only"):
                attrs += "R"
            if entry.get("system"):
                attrs += "S"
            rows.append(
                (
                    entry.get("name", ""),
                    entry.get("user", ""),
                    f"0x{int(entry.get('load', 0)):04X}",
                    f"0x{int(entry.get('exec', 0)):04X}",
                    f"{entry.get('size_kb', 0)} KB",
                    attrs,
                )
            )
        print_table(["File", "User", "Load", "Exec", "Size", "Attr"], rows)
    else:
        print("No files on disk.\n")

    show_key_values(
        "Space",
        {
            "total_kb": format_kb_value(data.get("total_kb", "")),
            "used_kb": format_kb_value(data.get("used_kb", "")),
            "free_kb": format_kb_value(data.get("free_kb", "")),
        },
        ["total_kb", "used_kb", "free_kb"],
    )


def format_response(payload):
    ok = bool(payload.get("ok"))
    command = payload.get("command", "")
    data = payload.get("data") or {}
    errors = payload.get("errors") or []

    if not ok:
        print("### Errors")
        rows = []
        for err in errors:
            rows.append((err.get("code", ""), err.get("message", "")))
        if rows:
            print_table(["Code", "Message"], rows)
        else:
            print("Error without details.")
        return

    if command == "new":
        show_key_values("Summary", {
            "dsk": data.get("dsk", ""),
            "total_kb": format_kb_value(data.get("total_kb", "")),
            "used_kb": format_kb_value(data.get("used_kb", "")),
            "free_kb": format_kb_value(data.get("free_kb", "")),
        }, ["dsk", "total_kb", "used_kb", "free_kb"])
        return

    if command == "free":
        show_key_values("Free Space", {
            "dsk": data.get("dsk", ""),
            "total_kb": format_kb_value(data.get("total_kb", "")),
            "used_kb": format_kb_value(data.get("used_kb", "")),
            "free_kb": format_kb_value(data.get("free_kb", "")),
        }, ["dsk", "total_kb", "used_kb", "free_kb"])
        return

    if command == "cat":
        format_cat(data)
        return

    if command in {"save", "get", "era"}:
        show_key_values(f"Result: {command}", data)
        return

    if "content" in data:
        print("### Content")
        print("```text")
        content = data.get("content", "")
        if content:
            print(str(content).rstrip("\n"))
        print("```\n")
        
        # METADATA TABLE - Commented out but can be re-enabled
        # Uncomment the lines below to show content metadata
        # show_key_values(
        #     "Metadata",
        #     {
        #         "type": data.get("content_type", data.get("detected_type", "")),
        #         "encoding": data.get("encoding", ""),
        #         "lines": data.get("line_count", ""),
        #         "bytes": data.get("bytes", ""),
        #     },
        #     ["type", "encoding", "lines", "bytes"],
        # )
        return

    show_key_values(f"Result: {command}", data)


json_path = Path(sys.argv[1])
text = json_path.read_text(encoding="utf-8", errors="replace").strip()
if not text:
    raise SystemExit(2)

payload = json.loads(text)
format_response(payload)
PY
}

resolved_binary="$(resolve_binary)"

tmp_out="$(mktemp)"
tmp_err="$(mktemp)"

set +e
"$resolved_binary" "${args[@]}" >"$tmp_out" 2>"$tmp_err"
status=$?
set -e

if [[ "$output_format" == "json" ]]; then
	if [[ -s "$tmp_out" ]]; then
		cat "$tmp_out"
	fi
else
	rendered=false
	if [[ -s "$tmp_out" ]]; then
		if render_markdown "$tmp_out" 2>/dev/null; then
			rendered=true
		fi
	fi

	if [[ "$rendered" == false && -s "$tmp_out" ]]; then
		cat <<'MD'
Could not format iaDSK output.
MD
	fi
fi

if [[ -s "$tmp_err" ]]; then
	cat "$tmp_err" >&2
fi

rm -f "$tmp_out" "$tmp_err"
exit $status

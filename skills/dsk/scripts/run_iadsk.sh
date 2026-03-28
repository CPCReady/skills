#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

binary=""
output_format="json"
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
		output_format="markdown"
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

is_binary_file() {
	local file="$1"
	if [[ ! -f "$file" ]]; then
		return 1
	fi
	if file "$file" 2>/dev/null | grep -qi "text\|ascii"; then
		return 1
	fi
	local ext="${file##*.}"
	local ext_lower
	ext_lower="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
	case "$ext_lower" in
	bas | txt | asm | s | inc | h)
		return 1
		;;
	*)
		return 0
		;;
	esac
}

prompt_for_dsk_name() {
	local command="$1"

	# Check if --dsk argument is present
	local has_dsk=false
	for arg in "${args[@]}"; do
		if [[ "$arg" == "--dsk" ]]; then
			has_dsk=true
			break
		fi
	done

	if [[ "$has_dsk" == true ]]; then
		return
	fi

	# Check if running in interactive mode
	if [[ ! -t 0 ]]; then
		echo "ERROR: El comando '$command' requiere --dsk <nombre.dsk>" >&2
		echo "Ejemplo: --dsk demo.dsk" >&2
		exit 1
	fi

	# Prompt for DSK name
	echo "" >&2
	echo "### Nombre de imagen DSK" >&2
	echo "" >&2

	local dsk_name=""
	while true; do
		read -r -p "Nombre del archivo DSK: " dsk_name
		if [[ -n "$dsk_name" ]]; then
			# Add .dsk extension if not present
			if [[ ! "$dsk_name" =~ \.dsk$ ]]; then
				dsk_name="${dsk_name}.dsk"
			fi
			break
		fi
		echo "⚠️  El nombre del archivo DSK es OBLIGATORIO. Por favor, ingresa un valor." >&2
		echo "" >&2
	done

	# Insert --dsk argument into args array
	local new_args=()
	new_args+=("${args[0]}") # command (save, new, cat, etc.)
	new_args+=("--dsk")
	new_args+=("$dsk_name")
	# Add remaining args
	for ((i = 1; i < ${#args[@]}; i++)); do
		new_args+=("${args[$i]}")
	done
	args=("${new_args[@]}")
}

prompt_for_load_address() {
	local file="$1"

	echo "### Añadir archivo binario" >&2
	echo "" >&2
	echo "Archivo: \`$file\`" >&2
	echo "" >&2
	echo "Para archivos binarios es OBLIGATORIO indicar la dirección de carga AMSDOS." >&2
	echo "" >&2

	while true; do
		read -r -p "Dirección de carga (--load) en hexadecimal: " load_addr
		if [[ -n "$load_addr" ]]; then
			echo "$load_addr"
			return 0
		fi
		echo "ERROR: La dirección de carga es obligatoria para archivos binarios." >&2
		echo "" >&2
	done
}

prompt_for_exec_address() {
	local file="$1"

	echo "" >&2
	echo "Dirección de ejecución (--exec) en hexadecimal." >&2
	echo "OBLIGATORIO para programas ejecutables. Dejar vacío solo para datos." >&2
	echo "" >&2

	read -r -p "Dirección de ejecución (--exec): " exec_addr

	echo "$exec_addr"
}

prompt_for_file_type() {
	local file="$1"
	local is_binary="$2"

	echo "" >&2
	echo "Tipo de archivo AMSDOS:" >&2
	echo "  1) ascii   - Archivo de texto ASCII" >&2
	echo "  2) binary  - Archivo binario con cabecera AMSDOS" >&2
	echo "  3) raw     - Datos crudos sin cabecera" >&2
	echo "" >&2

	if [[ "$is_binary" == "true" ]]; then
		read -r -p "Selecciona tipo [2]: " file_type
		file_type="${file_type:-2}"
	else
		read -r -p "Selecciona tipo [1]: " file_type
		file_type="${file_type:-1}"
	fi

	case "$file_type" in
	1)
		echo "ascii"
		;;
	2)
		echo "binary"
		;;
	3)
		echo "raw"
		;;
	*)
		echo "binary"
		;;
	esac
}

check_file_exists_in_dsk() {
	local dsk_file="$1"
	local filename="$2"
	local binary="$3"

	if [[ ! -f "$dsk_file" ]]; then
		return 1
	fi

	local tmp_cat
	tmp_cat="$(mktemp)"

	set +e
	"$binary" cat --dsk "$dsk_file" >"$tmp_cat" 2>/dev/null
	local status=$?
	set -e

	if [[ $status -ne 0 ]]; then
		rm -f "$tmp_cat"
		return 1
	fi

	local filename_upper
	filename_upper="$(basename "$filename" | tr '[:lower:]' '[:upper:]')"

	if grep -q "\"name\":\"$filename_upper\"" "$tmp_cat" 2>/dev/null; then
		rm -f "$tmp_cat"
		return 0
	fi

	rm -f "$tmp_cat"
	return 1
}

prompt_for_overwrite() {
	local filename="$1"

	echo "" >&2
	echo "⚠️  El archivo '$filename' ya existe en el disco." >&2
	echo "" >&2

	read -r -p "¿Deseas sobrescribir? (s/n) [n]: " overwrite
	overwrite="${overwrite:-n}"

	case "$overwrite" in
	s | S | y | Y)
		return 0
		;;
	*)
		return 1
		;;
	esac
}

process_save_command() {
	local new_args=()
	local has_save=false
	local has_file=false
	local has_load=false
	local has_exec=false
	local has_type=false
	local has_force=false
	local has_dsk=false
	local file_path=""
	local dsk_path=""
	local i=0

	# First pass: collect existing arguments
	while [[ $i -lt ${#args[@]} ]]; do
		case "${args[$i]}" in
		save | import)
			has_save=true
			new_args+=("${args[$i]}")
			;;
		--file)
			has_file=true
			file_path="${args[$((i + 1))]:-}"
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--dsk)
			has_dsk=true
			dsk_path="${args[$((i + 1))]:-}"
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--load)
			has_load=true
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--exec)
			has_exec=true
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--type)
			has_type=true
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--force)
			has_force=true
			new_args+=("${args[$i]}")
			;;
		*)
			new_args+=("${args[$i]}")
			;;
		esac
		i=$((i + 1))
	done

	# Only process if this is a save command with file specified
	if [[ "$has_save" != true || "$has_file" != true || -z "$file_path" ]]; then
		args=("${new_args[@]}")
		return
	fi

	# Check if we're in interactive mode
	local interactive=false
	if [[ -t 0 ]]; then
		interactive=true
	fi

	# Step 1: Determine if file is binary
	local file_is_binary=false
	if is_binary_file "$file_path"; then
		file_is_binary=true
	fi

	# Step 2: Prompt for file type if not specified
	if [[ "$has_type" == false && "$interactive" == true ]]; then
		echo "" >&2
		local file_type
		file_type=$(prompt_for_file_type "$file_path" "$file_is_binary")
		new_args+=("--type" "$file_type")
	fi

	# Step 3: For binary files, require load address
	if [[ "$file_is_binary" == true && "$has_load" == false ]]; then
		if [[ "$interactive" == true ]]; then
			echo "" >&2
			echo "Detectado archivo binario sin dirección de carga." >&2
			local load_addr
			load_addr=$(prompt_for_load_address "$file_path")
			new_args+=("--load" "$load_addr")
		else
			echo "ERROR: Archivos binarios requieren --load <dirección>." >&2
			echo "Ejemplo: --load 0x4000" >&2
			exit 1
		fi
	fi

	# Step 4: For binary files, prompt for exec address if not specified
	if [[ "$file_is_binary" == true && "$has_exec" == false && "$interactive" == true ]]; then
		local exec_addr
		exec_addr=$(prompt_for_exec_address "$file_path")
		if [[ -n "$exec_addr" ]]; then
			new_args+=("--exec" "$exec_addr")
		fi
		echo "" >&2
	fi

	args=("${new_args[@]}")
}

check_overwrite_if_needed() {
	local binary="$1"
	local new_args=()
	local has_save=false
	local has_file=false
	local has_dsk=false
	local has_force=false
	local file_path=""
	local dsk_path=""
	local i=0

	# Parse arguments to check if this is a save command
	while [[ $i -lt ${#args[@]} ]]; do
		case "${args[$i]}" in
		save | import)
			has_save=true
			new_args+=("${args[$i]}")
			;;
		--file)
			has_file=true
			file_path="${args[$((i + 1))]:-}"
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--dsk)
			has_dsk=true
			dsk_path="${args[$((i + 1))]:-}"
			new_args+=("${args[$i]}" "${args[$((i + 1))]:-}")
			i=$((i + 1))
			;;
		--force)
			has_force=true
			new_args+=("${args[$i]}")
			;;
		*)
			new_args+=("${args[$i]}")
			;;
		esac
		i=$((i + 1))
	done

	# Only check overwrite if this is a save command with file and dsk specified
	if [[ "$has_save" != true || "$has_file" != true || "$has_dsk" != true ]]; then
		return
	fi

	# Only check in interactive mode
	if [[ ! -t 0 ]]; then
		return
	fi

	# Skip if --force already provided
	if [[ "$has_force" == true ]]; then
		return
	fi

	# Check if file exists in DSK
	local filename
	filename="$(basename "$file_path")"

	if check_file_exists_in_dsk "$dsk_path" "$filename" "$binary"; then
		if prompt_for_overwrite "$filename"; then
			args=("${new_args[@]}" "--force")
		else
			echo "" >&2
			echo "Operación cancelada por el usuario." >&2
			exit 0
		fi
	fi
}

# Check if DSK name is required and prompt if missing
if [[ ${#args[@]} -gt 0 ]]; then
	command="${args[0]}"
	case "$command" in
	help | --help | -h)
		# help doesn't need --dsk
		;;
	*)
		# All other commands need --dsk
		prompt_for_dsk_name "$command"
		;;
	esac
fi

process_save_command

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

check_overwrite_if_needed "$resolved_binary"

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

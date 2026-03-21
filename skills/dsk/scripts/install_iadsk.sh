#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

json=false
install_dir=""

json_escape() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    printf '%s' "$value"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-dir)
            shift
            if [[ $# -eq 0 ]]; then
                echo "Missing value for --install-dir" >&2
                exit 1
            fi
            install_dir="$1"
            ;;
        --json)
            json=true
            ;;
        -h|--help)
            cat <<'USAGE'
Usage: install_iadsk.sh [--install-dir <path>] [--json]
USAGE
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
    shift
done

uname_s="$(uname -s)"
uname_m="$(uname -m)"

case "$uname_s" in
    Darwin)
        platform="macos"
        ;;
    Linux)
        platform="linux"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        platform="windows"
        ;;
    *)
        platform="${uname_s,,}"
        ;;
esac

case "$uname_m" in
    x86_64|amd64)
        arch="x64"
        ;;
    arm64|aarch64)
        arch="arm64"
        ;;
    *)
        arch="${uname_m,,}"
        ;;
esac

if [[ -z "$install_dir" ]]; then
    if [[ "$platform" == "windows" ]]; then
        install_dir="${USERPROFILE:-$HOME}/bin"
    else
        install_dir="$HOME/.local/bin"
    fi
fi

binary_name="iaDSK"
if [[ "$platform" == "windows" ]]; then
    binary_name="iaDSK.exe"
fi

source_binary="$SKILL_ROOT/assets/bin/${platform}-${arch}/${binary_name}"
if [[ ! -f "$source_binary" ]]; then
    msg="No bundled iaDSK binary for ${platform}-${arch}. Expected: ${source_binary}"
    if [[ "$json" == true ]]; then
        printf '{"ok":false,"system":"%s","arch":"%s","error":"%s"}\n' "$platform" "$arch" "$(json_escape "$msg")" >&2
    else
        echo "$msg" >&2
    fi
    exit 1
fi

mkdir -p "$install_dir"
installed_binary="$install_dir/$binary_name"
cp "$source_binary" "$installed_binary"

if [[ "$platform" != "windows" ]]; then
    chmod +x "$installed_binary"
fi

if [[ "$json" == true ]]; then
    printf '{"ok":true,"system":"%s","arch":"%s","source_binary":"%s","installed_binary":"%s"}\n' \
        "$platform" "$arch" "$(json_escape "$source_binary")" "$(json_escape "$installed_binary")"
else
    echo "iaDSK instalado en: $installed_binary"
fi

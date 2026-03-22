#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

iadsk_script="$SCRIPT_DIR/iadsk.py"

resolve_python() {
	if command -v python3 >/dev/null 2>&1; then
		echo "python3"
		return 0
	fi

	if command -v python >/dev/null 2>&1; then
		echo "python"
		return 0
	fi

	echo "Python 3 no está disponible. Instala Python 3 para usar iadsk.py." >&2
	return 1
}

if [[ ! -f "$iadsk_script" ]]; then
	echo "Error: iadsk.py no encontrado en $iadsk_script" >&2
	exit 1
fi

PYTHON_CMD=""
resolve_python
if [[ -z "$PYTHON_CMD" ]]; then
	PYTHON_CMD="python3"
fi

exec "$PYTHON_CMD" "$iadsk_script" "$@"

#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# run_rvm.sh — Wrapper para Retro Virtual Machine 2 (Amstrad CPC)
#
# Requisito: Variable de entorno RETRO_VIRTUAL_MACHINE_PATH apuntando al
# binario de RVM v2.0 BETA-1 r7.
#
# Uso:
#   run_rvm.sh [--machine <id>] [--warp] [--noshader] [--command <text>]
#              [--width <px>] [--] [<archivo>]
#
#   Tipos de archivo reconocidos:
#     .dsk         → máquina por defecto: cpc6128
#     .cdt / .tzx  → máquina por defecto: cpc464
#     .bin         → pide máquina, dirección de carga y dirección de salto
#     .sna / .z80  → pide máquina, carga como snapshot
#     (sin archivo) → pide máquina, arranca en modo standalone vacío
# ---------------------------------------------------------------------------

REQUIRED_VERSION="v2.0 BETA-1 r7"

# ---------------------------------------------------------------------------
# 1. Verificar variable de entorno
# ---------------------------------------------------------------------------
if [[ -z "${RETRO_VIRTUAL_MACHINE_PATH:-}" ]]; then
	echo "ERROR: Variable de entorno RETRO_VIRTUAL_MACHINE_PATH no definida." >&2
	echo "Ejemplo: export RETRO_VIRTUAL_MACHINE_PATH=\"/Applications/Retro Virtual Machine 2.app/Contents/MacOS/Retro Virtual Machine 2\"" >&2
	exit 1
fi

RVM_BIN="$RETRO_VIRTUAL_MACHINE_PATH"

if [[ ! -f "$RVM_BIN" ]]; then
	echo "ERROR: Binario de RVM no encontrado en: $RVM_BIN" >&2
	exit 1
fi

if [[ ! -x "$RVM_BIN" ]]; then
	echo "ERROR: El binario de RVM no tiene permisos de ejecución: $RVM_BIN" >&2
	exit 1
fi

# ---------------------------------------------------------------------------
# 2. Verificar versión
# RVM emite códigos de escape ANSI en su cabecera — se eliminan antes de comparar
# La versión aparece en las primeras líneas del output de --help
# ---------------------------------------------------------------------------
RVM_VERSION_BLOCK=$("$RVM_BIN" --help 2>&1 | head -5 | sed 's/\x1b\[[0-9;]*m//g' || true)

if [[ "$RVM_VERSION_BLOCK" != *"$REQUIRED_VERSION"* ]]; then
	RVM_VERSION_CLEAN=$(echo "$RVM_VERSION_BLOCK" | tr -d '\n' | tr -s ' ')
	echo "ERROR: Versión de Retro Virtual Machine no compatible." >&2
	echo "  Requerida : $REQUIRED_VERSION" >&2
	echo "  Detectada : $RVM_VERSION_CLEAN" >&2
	exit 1
fi

# ---------------------------------------------------------------------------
# 3. Parsear argumentos del wrapper
# ---------------------------------------------------------------------------
machine=""
extra_args=()
input_file=""
has_double_dash=false
close_existing_flag=false

while [[ $# -gt 0 ]]; do
	case "$1" in
	--close-existing | -ce)
		close_existing_flag=true
		;;
	--machine | -m)
		shift
		if [[ $# -eq 0 ]]; then
			echo "ERROR: --machine requiere un valor (ej: cpc464, cpc6128, cpc664)" >&2
			exit 1
		fi
		machine="$1"
		;;
	--warp | -w)
		extra_args+=("--warp")
		;;
	--noshader | -ns)
		extra_args+=("--noshader")
		;;
	--command | -c)
		shift
		if [[ $# -eq 0 ]]; then
			echo "ERROR: --command requiere un valor" >&2
			exit 1
		fi
		# Añadir retorno de carro al final del comando si no lo tiene ya
		cmd_value="$1"
		if [[ "$cmd_value" != *$'\n' ]]; then
			cmd_value="${cmd_value}"$'\n'
		fi
		extra_args+=("--command=${cmd_value}")
		;;
	--width | -wi)
		shift
		if [[ $# -eq 0 ]]; then
			echo "ERROR: --width requiere un valor numérico (mínimo 700)" >&2
			exit 1
		fi
		extra_args+=("--width=$1")
		;;
	--play | -p)
		extra_args+=("--play")
		;;
	--)
		has_double_dash=true
		shift
		# El resto son argumentos directos a RVM sin procesar
		extra_args+=("$@")
		break
		;;
	-h | --help)
		cat <<'USAGE'
Uso: run_rvm.sh [opciones] [<archivo>]

Opciones:
  --machine, -m <id>      Máquina CPC (cpc464, cpc664, cpc6128). Por defecto
                          según tipo de archivo: .dsk→cpc6128, .cdt/.tzx→cpc464
  --warp, -w              Modo acelerado (sin límite de velocidad)
  --noshader, -ns         Desactivar shader de pantalla
  --command, -c <texto>   Enviar teclas al intérprete BASIC al arrancar
  --width, -wi <px>       Ancho de ventana (mínimo 700)
  --play, -p              Auto play de cinta al inicio
  --close-existing, -ce   Cerrar instancias de RVM abiertas sin preguntar
  --                      Pasar argumentos directamente a RVM sin procesar
  -h, --help              Mostrar esta ayuda

Tipos de archivo:
  .dsk              Imagen de disco  → máquina por defecto: cpc6128
  .cdt / .tzx       Cinta de cassette → máquina por defecto: cpc464
  .bin              Binario           → pide máquina, dirección carga y salto
  .sna / .z80       Snapshot          → pide máquina

Variable de entorno:
  RETRO_VIRTUAL_MACHINE_PATH  Ruta al binario de RVM (obligatoria)

USAGE
		exit 0
		;;
	-*)
		echo "ERROR: Opción desconocida: $1" >&2
		echo "Usa --help para ver las opciones disponibles." >&2
		exit 1
		;;
	*)
		if [[ -n "$input_file" ]]; then
			echo "ERROR: Solo se puede especificar un archivo." >&2
			exit 1
		fi
		input_file="$1"
		;;
	esac
	shift
done

# ---------------------------------------------------------------------------
# 4. Helper: verificar modo interactivo
# ---------------------------------------------------------------------------
require_interactive() {
	local context="$1"
	if [[ ! -t 0 ]]; then
		echo "ERROR: $context requiere un terminal interactivo." >&2
		echo "Proporciona los parámetros necesarios explícitamente." >&2
		exit 1
	fi
}

# ---------------------------------------------------------------------------
# 5. Helper: preguntar máquina
# ---------------------------------------------------------------------------
prompt_for_machine() {
	require_interactive "Selección de máquina CPC"
	echo "" >&2
	echo "### Máquina CPC" >&2
	echo "" >&2
	echo "  1) cpc464   - Amstrad CPC 464 (cassette, 64K RAM)" >&2
	echo "  2) cpc664   - Amstrad CPC 664 (disco, 64K RAM)" >&2
	echo "  3) cpc6128  - Amstrad CPC 6128 (disco, 128K RAM)" >&2
	echo "" >&2

	local selection=""
	while true; do
		read -r -p "Selecciona máquina [1-3]: " selection
		case "$selection" in
		1 | cpc464)
			machine="cpc464"
			break
			;;
		2 | cpc664)
			machine="cpc664"
			break
			;;
		3 | cpc6128)
			machine="cpc6128"
			break
			;;
		*)
			echo "Selección inválida. Elige 1, 2 o 3." >&2
			;;
		esac
	done
}

# ---------------------------------------------------------------------------
# 6. Helper: preguntar dirección hexadecimal
# ---------------------------------------------------------------------------
prompt_for_address() {
	local label="$1"
	local varname="$2"
	local optional="${3:-false}"

	echo "" >&2
	if [[ "$optional" == "true" ]]; then
		echo "$label (hexadecimal, dejar vacío para omitir):" >&2
		read -r -p "> " addr_value
		printf '%s' "$addr_value"
	else
		local addr_value=""
		while true; do
			read -r -p "$label (hexadecimal): " addr_value
			if [[ -n "$addr_value" ]]; then
				printf '%s' "$addr_value"
				return 0
			fi
			echo "ERROR: $label es obligatoria." >&2
		done
	fi
}

# ---------------------------------------------------------------------------
# 7. Determinar tipo de archivo y construir comando RVM
# ---------------------------------------------------------------------------
rvm_args=()

if [[ "$has_double_dash" == true ]]; then
	# Modo pass-through: los args ya están en extra_args, solo necesitamos máquina si no se dio
	if [[ -z "$machine" ]]; then
		prompt_for_machine
	fi
	rvm_args+=("--boot=$machine")
	rvm_args+=("${extra_args[@]}")
else
	# Modo normal: detectar por extensión
	if [[ -z "$input_file" ]]; then
		# Sin archivo: solo arrancar la máquina
		if [[ -z "$machine" ]]; then
			prompt_for_machine
		fi
		rvm_args+=("--boot=$machine")
		rvm_args+=("${extra_args[@]}")
	else
		# Verificar que el archivo existe
		if [[ ! -f "$input_file" ]]; then
			echo "ERROR: Archivo no encontrado: $input_file" >&2
			exit 1
		fi

		# Detectar extensión (en minúsculas)
		ext="${input_file##*.}"
		ext_lower="${ext,,}"

		case "$ext_lower" in

		# --- Disco DSK ---
		dsk)
			if [[ -z "$machine" ]]; then
				machine="cpc6128"
			fi
			rvm_args+=("--boot=$machine")
			rvm_args+=("--insert" "$input_file")
			rvm_args+=("${extra_args[@]}")
			;;

		# --- Cinta CDT / TZX ---
		cdt | tzx)
			if [[ -z "$machine" ]]; then
				machine="cpc464"
			fi
			rvm_args+=("--boot=$machine")
			rvm_args+=("--insert" "$input_file")
			rvm_args+=("${extra_args[@]}")
			;;

		# --- Binario .bin ---
		bin)
			if [[ -z "$machine" ]]; then
				prompt_for_machine
			fi
			require_interactive "Carga de archivo binario"

			echo "" >&2
			echo "### Cargar archivo binario" >&2
			echo "" >&2
			echo "Archivo: \`$input_file\`" >&2
			echo "Para archivos binarios es OBLIGATORIO indicar la dirección de carga y de salto." >&2

			load_addr=$(prompt_for_address "Dirección de carga (--load)" "load_addr")
			jump_addr=$(prompt_for_address "Dirección de salto (--jump)" "jump_addr")

			rvm_args+=("--boot=$machine")
			rvm_args+=("--load=$load_addr" "$input_file")
			rvm_args+=("--jump=$jump_addr")
			rvm_args+=("${extra_args[@]}")
			;;

		# --- Snapshot .sna / .z80 ---
		sna | z80)
			if [[ -z "$machine" ]]; then
				prompt_for_machine
			fi
			rvm_args+=("--boot=$machine")
			rvm_args+=("--snapshot" "$input_file")
			rvm_args+=("${extra_args[@]}")
			;;

		# --- Extensión desconocida ---
		*)
			echo "ERROR: Extensión de archivo no reconocida: .$ext_lower" >&2
			echo "Tipos soportados: .dsk, .cdt, .tzx, .bin, .sna, .z80" >&2
			echo "Usa -- para pasar argumentos directamente a RVM." >&2
			exit 1
			;;
		esac
	fi
fi

# ---------------------------------------------------------------------------
# 8. Verificar instancias abiertas de RVM
# ---------------------------------------------------------------------------
RVM_BINARY_NAME="$(basename "$RVM_BIN")"

# Leer PIDs en array — compatible con bash 3+ (macOS default)
RVM_PIDS=()
while IFS= read -r pid; do
	[[ -n "$pid" ]] && RVM_PIDS+=("$pid")
done < <(pgrep -f "$RVM_BINARY_NAME" 2>/dev/null || true)

if [[ ${#RVM_PIDS[@]} -gt 0 ]]; then
	PID_COUNT="${#RVM_PIDS[@]}"
	if [[ "$close_existing_flag" == true ]]; then
		# Modo no interactivo con flag explícito: cerrar sin preguntar
		for pid in "${RVM_PIDS[@]}"; do
			kill -9 "$pid" 2>/dev/null || true
		done
	elif [[ -t 0 ]]; then
		# Modo interactivo: preguntar al usuario
		echo "" >&2
		echo "### Instancias de RVM en ejecución: $PID_COUNT" >&2
		echo "" >&2
		for pid in "${RVM_PIDS[@]}"; do
			echo "  PID $pid" >&2
		done
		echo "" >&2
		read -r -p "¿Cerrar instancias existentes antes de lanzar? (s/n) [n]: " close_existing
		close_existing="${close_existing:-n}"
		case "$close_existing" in
		s | S | y | Y)
			for pid in "${RVM_PIDS[@]}"; do
				kill -9 "$pid" 2>/dev/null || true
			done
			echo "" >&2
			;;
		esac
	fi
fi

# ---------------------------------------------------------------------------
# 9. Lanzar RVM en background
# ---------------------------------------------------------------------------
"$RVM_BIN" "${rvm_args[@]}" &
disown

exit 0

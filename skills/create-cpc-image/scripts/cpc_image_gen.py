#!/usr/bin/env python3
"""
cpc_image_gen.py — Generador de imágenes pixel art para Amstrad CPC.

Genera imágenes PNG respetando las restricciones técnicas de los tres
modos gráficos del CPC: resolución máxima y número de colores simultáneos.

Uso:
    python cpc_image_gen.py --mode 1 --width 320 --height 200 \
        --colors "0,9,18,26" --output /ruta/imagen.png

    python cpc_image_gen.py --list-colors
    python cpc_image_gen.py --list-modes

El script recibe los pixels ya calculados como datos JSON en stdin,
o genera una imagen en blanco (útil para test).
"""

import argparse
import json
import math
import os
import sys
import time
from typing import List, Optional, Tuple

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print(
        "ERROR: Pillow y numpy son requeridos. Activa el venv e instálalos.",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Paleta oficial Amstrad CPC — 27 colores
# ---------------------------------------------------------------------------

CPC_PALETTE = {
    0: (0, 0, 0, "Negro"),
    1: (0, 0, 128, "Azul"),
    2: (0, 0, 255, "Azul intenso"),
    3: (128, 0, 0, "Rojo"),
    4: (128, 0, 128, "Magenta"),
    5: (128, 0, 255, "Malva"),
    6: (255, 0, 0, "Rojo intenso"),
    7: (255, 0, 128, "Morado"),
    8: (255, 0, 255, "Magenta intenso"),
    9: (0, 128, 0, "Verde"),
    10: (0, 128, 128, "Cyan"),
    11: (0, 128, 255, "Azul celeste"),
    12: (128, 128, 0, "Amarillo"),
    13: (128, 128, 128, "Blanco"),
    14: (128, 128, 255, "Azul pastel"),
    15: (255, 128, 0, "Anaranjado"),
    16: (255, 128, 128, "Rosado"),
    17: (255, 128, 255, "Magenta pastel"),
    18: (0, 255, 0, "Verde intenso"),
    19: (0, 255, 128, "Verde mar"),
    20: (0, 255, 255, "Cyan intenso"),
    21: (128, 255, 0, "Verde lima"),
    22: (128, 255, 128, "Verde pastel"),
    23: (128, 255, 255, "Cyan pastel"),
    24: (255, 255, 0, "Amarillo intenso"),
    25: (255, 255, 128, "Amarillo pastel"),
    26: (255, 255, 255, "Blanco intenso"),
}

# ---------------------------------------------------------------------------
# Especificaciones de modos gráficos CPC
# ---------------------------------------------------------------------------

CPC_MODES = {
    0: {
        "width": 160,
        "height": 200,
        "colors": 16,
        "desc": "160×200, 16 colores simultáneos",
    },
    1: {
        "width": 320,
        "height": 200,
        "colors": 4,
        "desc": "320×200, 4 colores simultáneos",
    },
    2: {
        "width": 640,
        "height": 200,
        "colors": 2,
        "desc": "640×200, 2 colores simultáneos",
    },
}


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------


def get_rgb(color_id: int) -> Tuple[int, int, int]:
    """Devuelve la tupla RGB de un color CPC dado su ID (0-26)."""
    if color_id not in CPC_PALETTE:
        raise ValueError(f"Color {color_id} no existe. Rango válido: 0-26.")
    r, g, b, _ = CPC_PALETTE[color_id]
    return r, g, b


def nearest_cpc_color(r: int, g: int, b: int) -> int:
    """Encuentra el color CPC más cercano a un RGB arbitrario (distancia euclidiana)."""
    best_id = 0
    best_dist = float("inf")
    for cid, (cr, cg, cb, _) in CPC_PALETTE.items():
        dist = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_id = cid
    return best_id


def validate_mode(mode: int) -> None:
    if mode not in CPC_MODES:
        raise ValueError(f"Modo {mode} inválido. Usa 0, 1 o 2.")


def validate_dimensions(mode: int, width: int, height: int) -> None:
    max_w = CPC_MODES[mode]["width"]
    max_h = CPC_MODES[mode]["height"]
    if width > max_w or height > max_h:
        raise ValueError(
            f"Modo {mode}: resolución máxima {max_w}×{max_h}. Pedido: {width}×{height}."
        )
    if width < 1 or height < 1:
        raise ValueError("Ancho y alto deben ser al menos 1 píxel.")


def validate_colors(mode: int, color_ids: List[int]) -> None:
    max_colors = CPC_MODES[mode]["colors"]
    unique = list(dict.fromkeys(color_ids))  # preserva orden, elimina duplicados
    if len(unique) > max_colors:
        raise ValueError(
            f"Modo {mode} permite máximo {max_colors} colores simultáneos. "
            f"Se proporcionaron {len(unique)}: {unique}"
        )
    for cid in unique:
        if cid not in CPC_PALETTE:
            raise ValueError(f"Color {cid} no existe en la paleta CPC (0-26).")


def reduce_to_palette(image_rgb: np.ndarray, allowed_colors: List[int]) -> np.ndarray:
    """
    Reduce cada píxel de image_rgb al color CPC más cercano dentro de allowed_colors.
    image_rgb shape: (H, W, 3)
    Devuelve array (H, W, 3) con colores cuantizados.
    """
    palette_rgb = np.array([get_rgb(c) for c in allowed_colors], dtype=np.float32)
    h, w, _ = image_rgb.shape
    flat = image_rgb.reshape(-1, 3).astype(np.float32)

    # Vectorizado: distancia euclidiana a cada color de la paleta
    dists = np.linalg.norm(flat[:, None, :] - palette_rgb[None, :, :], axis=2)
    best_idx = np.argmin(dists, axis=1)
    result = palette_rgb[best_idx].astype(np.uint8)
    return result.reshape(h, w, 3)


# ---------------------------------------------------------------------------
# Generador principal
# ---------------------------------------------------------------------------


class CPCImageGenerator:
    """
    Genera imágenes PNG pixel art respetando las restricciones del Amstrad CPC.

    Acepta datos de píxeles como matriz 2D de IDs de color CPC, o crea
    una imagen en blanco con la paleta indicada.
    """

    def __init__(
        self,
        mode: int,
        width: Optional[int] = None,
        height: Optional[int] = None,
        colors: Optional[List[int]] = None,
    ):
        validate_mode(mode)
        self.mode = mode
        self.spec = CPC_MODES[mode]

        self.width = width if width is not None else self.spec["width"]
        self.height = height if height is not None else self.spec["height"]
        validate_dimensions(mode, self.width, self.height)

        max_c = self.spec["colors"]
        if colors is None:
            # Colores por defecto: primeros N de la paleta
            self.colors = list(range(max_c))
        else:
            validate_colors(mode, colors)
            self.colors = list(dict.fromkeys(colors))  # deduplicar

        self.image: Optional[Image.Image] = None

    def create_blank(self, background_color_id: int = 0) -> "CPCImageGenerator":
        """Crea una imagen en blanco con el color de fondo indicado."""
        if background_color_id not in self.colors:
            raise ValueError(
                f"El color de fondo {background_color_id} no está en la paleta activa: {self.colors}"
            )
        rgb = get_rgb(background_color_id)
        self.image = Image.new("RGB", (self.width, self.height), rgb)
        return self

    def from_pixel_matrix(self, matrix: List[List[int]]) -> "CPCImageGenerator":
        """
        Construye la imagen a partir de una matriz 2D de IDs de color CPC.
        matrix[y][x] = color_id (0-26)
        """
        if len(matrix) != self.height:
            raise ValueError(
                f"La matriz tiene {len(matrix)} filas, se esperaban {self.height}."
            )
        if any(len(row) != self.width for row in matrix):
            raise ValueError(f"Todas las filas deben tener {self.width} columnas.")

        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for y, row in enumerate(matrix):
            for x, cid in enumerate(row):
                if cid not in self.colors:
                    raise ValueError(
                        f"Pixel ({x},{y}) usa color {cid} que no está en la paleta activa: {self.colors}"
                    )
                img_array[y, x] = get_rgb(cid)

        self.image = Image.fromarray(img_array, "RGB")
        return self

    def from_rgb_image(self, source_path: str) -> "CPCImageGenerator":
        """
        Convierte una imagen RGB existente a la paleta CPC activa.
        Redimensiona al tamaño del generador si es necesario.
        """
        src = Image.open(source_path).convert("RGB")
        if src.size != (self.width, self.height):
            src = src.resize((self.width, self.height), Image.Resampling.LANCZOS)

        arr = np.array(src)
        quantized = reduce_to_palette(arr, self.colors)
        self.image = Image.fromarray(quantized, "RGB")
        return self

    def draw_pixel_block(
        self, x: int, y: int, color_id: int, block_size: int = 8
    ) -> None:
        """
        Dibuja un bloque de píxeles de block_size×block_size en (x, y).
        Las coordenadas son en unidades de bloque, no de píxel.
        """
        if self.image is None:
            raise RuntimeError(
                "Crea o carga una imagen primero (create_blank, from_pixel_matrix, etc.)."
            )
        if color_id not in self.colors:
            raise ValueError(
                f"Color {color_id} no está en la paleta activa: {self.colors}"
            )

        rgb = get_rgb(color_id)
        px_x = x * block_size
        px_y = y * block_size

        pixels = self.image.load()
        for dy in range(block_size):
            for dx in range(block_size):
                nx, ny = px_x + dx, px_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    pixels[nx, ny] = rgb

    def save(self, output_path: str) -> str:
        """Guarda la imagen como PNG. Devuelve la ruta absoluta del archivo."""
        if self.image is None:
            raise RuntimeError(
                "No hay imagen generada. Usa create_blank() o from_pixel_matrix()."
            )
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.image.save(output_path, "PNG")
        return os.path.abspath(output_path)

    def info(self) -> dict:
        """Devuelve un resumen de la configuración actual."""
        return {
            "mode": self.mode,
            "width": self.width,
            "height": self.height,
            "max_colors": self.spec["colors"],
            "active_colors": self.colors,
            "active_color_names": [CPC_PALETTE[c][3] for c in self.colors],
            "description": self.spec["desc"],
        }


# ---------------------------------------------------------------------------
# Nombre de archivo de salida
# ---------------------------------------------------------------------------


def build_output_filename(mode: int, output_dir: str) -> str:
    """Genera el nombre de archivo: cpc_{modo}_{timestamp}.png"""
    ts = int(time.time())
    filename = f"cpc_{mode}_{ts}.png"
    return os.path.join(output_dir, filename)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_color_list(s: str) -> List[int]:
    """Parsea '0,9,18,26' → [0, 9, 18, 26]"""
    try:
        return [int(x.strip()) for x in s.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Lista de colores inválida: '{s}'. Usa números separados por coma (ej: 0,9,18,26)."
        )


def cmd_list_colors() -> None:
    print("\nPaleta Amstrad CPC — 27 colores\n")
    print(f"{'ID':>3}  {'Nombre':<20}  {'Hex':>8}  {'RGB'}")
    print("-" * 55)
    for cid, (r, g, b, name) in CPC_PALETTE.items():
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        print(f"{cid:>3}  {name:<20}  {hex_color}  ({r:3}, {g:3}, {b:3})")
    print()


def cmd_list_modes() -> None:
    print("\nModos gráficos Amstrad CPC\n")
    print(f"{'Modo':>5}  {'Resolución':>12}  {'Colores':>8}  Descripción")
    print("-" * 55)
    for m, spec in CPC_MODES.items():
        print(
            f"{m:>5}  {spec['width']:>6}×{spec['height']:<5}  {spec['colors']:>8}  {spec['desc']}"
        )
    print()


def cmd_generate(args: argparse.Namespace) -> None:
    mode = args.mode
    width = args.width
    height = args.height
    colors = parse_color_list(args.colors) if args.colors else None
    output_dir = args.output_dir or os.getcwd()

    # Construir generador
    gen = CPCImageGenerator(mode=mode, width=width, height=height, colors=colors)

    # Leer datos de píxeles desde stdin si se proporcionan
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    gen.from_pixel_matrix(data)
                else:
                    print(
                        "ERROR: stdin debe ser una matriz JSON 2D de IDs de color.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON inválido en stdin: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            gen.create_blank(background_color_id=gen.colors[0])
    else:
        gen.create_blank(background_color_id=gen.colors[0])

    # Guardar
    output_path = build_output_filename(mode, output_dir)
    if args.output:
        output_path = args.output

    saved = gen.save(output_path)

    # Output JSON para el agente
    result = {
        "ok": True,
        "file": saved,
        "mode": mode,
        "width": gen.width,
        "height": gen.height,
        "colors": gen.colors,
        "color_names": [CPC_PALETTE[c][3] for c in gen.colors],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generador de imágenes pixel art para Amstrad CPC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Crear imagen en blanco modo 1 (320×200, 4 colores)
  python cpc_image_gen.py --mode 1 --colors "0,9,18,26" --output-dir /tmp

  # Crear imagen modo 0 con tamaño personalizado
  python cpc_image_gen.py --mode 0 --width 80 --height 100 --colors "0,1,2,3"

  # Crear imagen desde matriz de píxeles JSON
  echo '[[0,1,0],[1,0,1]]' | python cpc_image_gen.py --mode 1 --width 3 --height 2

  # Listar todos los colores disponibles
  python cpc_image_gen.py --list-colors

  # Listar modos de pantalla
  python cpc_image_gen.py --list-modes
        """,
    )

    parser.add_argument(
        "--list-colors",
        action="store_true",
        help="Mostrar paleta completa de 27 colores CPC",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="Mostrar modos de pantalla disponibles",
    )

    parser.add_argument(
        "--mode", type=int, choices=[0, 1, 2], help="Modo gráfico CPC (0, 1 o 2)"
    )
    parser.add_argument(
        "--width", type=int, help="Ancho en píxeles (no superar máximo del modo)"
    )
    parser.add_argument(
        "--height", type=int, help="Alto en píxeles (no superar máximo del modo)"
    )
    parser.add_argument(
        "--colors",
        type=str,
        help="IDs de colores CPC separados por coma (ej: '0,9,18,26')",
    )
    parser.add_argument(
        "--output", type=str, help="Ruta completa del archivo de salida PNG"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        dest="output_dir",
        help="Directorio de salida (usa nombre automático)",
    )

    args = parser.parse_args()

    if args.list_colors:
        cmd_list_colors()
        return

    if args.list_modes:
        cmd_list_modes()
        return

    if args.mode is None:
        parser.error("Se requiere --mode (0, 1 o 2) para generar una imagen.")

    # Aplicar dimensiones por defecto del modo si no se especifican
    if args.width is None:
        args.width = CPC_MODES[args.mode]["width"]
    if args.height is None:
        args.height = CPC_MODES[args.mode]["height"]

    try:
        cmd_generate(args)
    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

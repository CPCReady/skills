---
name: create-cpc-image
description: Crear imágenes pixel art para Amstrad CPC en formato PNG. Usar cuando el usuario pida crear imágenes, sprites, personajes, escenas, fondos, gráficos o cualquier elemento visual en estilo pixel art para ordenadores Amstrad CPC. La skill genera imágenes PNG respetando las restricciones técnicas de los tres modos gráficos del CPC (resolución máxima y colores simultáneos). Preguntar siempre el modo CPC si el usuario no lo especifica. Activar también cuando el usuario diga "hazme un personaje CPC", "quiero una imagen para CPC", "dibuja en pixel art estilo Amstrad", o describa cualquier elemento visual para un juego o demo de CPC.
---

# create-cpc-image

Skill para generar imágenes pixel art auténticas para Amstrad CPC. El resultado
es siempre un archivo PNG con la resolución y paleta de colores correctas para
el modo CPC seleccionado.

## Flujo de trabajo

### 1. Interpretar la petición del usuario

Extrae de la descripción:
- **Tema**: personaje, escena, objeto, sprite, fondo, texto gráfico...
- **Modo CPC**: 0, 1 o 2. Si no se menciona, **preguntar siempre antes de generar**.
- **Tamaño**: si el usuario lo especifica, úsalo. Si no, usa la resolución máxima del modo.
- **Colores**: si el usuario menciona colores concretos, búscalos en la paleta CPC.

### 2. Preguntar el modo CPC (si no se especificó)

Antes de generar nada, presenta estas opciones:

```
¿En qué modo CPC quieres la imagen?

• Modo 0 — 160×200 píxeles, 16 colores simultáneos
  (Más colores, ideal para personajes detallados y escenas ricas)

• Modo 1 — 320×200 píxeles, 4 colores simultáneos
  (Equilibrado, el más usado en juegos de la época)

• Modo 2 — 640×200 píxeles, 2 colores simultáneos
  (Máxima resolución horizontal, solo 2 colores, ideal para texto y siluetas)
```

### 3. Seleccionar la paleta de colores

La paleta CPC tiene exactamente 27 colores disponibles (ver `references/cpc-colors.md`).
Para cada modo, elige los N colores simultáneos que mejor representen la descripción:

- **Modo 0**: elige hasta 16 colores de los 27
- **Modo 1**: elige exactamente 4 colores
- **Modo 2**: elige exactamente 2 colores

Consulta las combinaciones recomendadas en `references/cpc-colors.md` si necesitas
inspiración según el tipo de imagen (personaje, naturaleza, noche, etc.).

### 4. Diseñar la imagen como matriz de píxeles

**Este es el paso central y más importante.** Diseña la imagen mentalmente como
pixel art en una cuadrícula:

- Cada celda de la cuadrícula es un píxel CPC
- Usa solo los colores elegidos para ese modo
- Respeta la resolución máxima del modo (nunca superarla)
- Mantén proporciones y formas reconocibles dentro de las limitaciones
- Piensa en bloques de 8×8 píxeles como unidad visual básica

El diseño se expresa como una matriz JSON 2D donde cada valor es el ID de color CPC:

```json
[
  [0, 0, 26, 26, 0, 0],
  [0, 26, 15, 15, 26, 0],
  [26, 15, 15, 15, 15, 26],
  [0, 26, 15, 15, 26, 0],
  [0, 0, 26, 26, 0, 0]
]
```

Para imágenes grandes (resolución completa), genera la matriz completa.
Para personajes o sprites, puedes trabajar con una subregión y rellenar
el resto con el color de fondo.

### 5. Generar la imagen con el script

**Script**: `scripts/cpc_image_gen.py`  
**Python**: usar siempre el intérprete del venv: `venv/bin/python3`

```bash
# Generar imagen desde matriz de píxeles JSON (stdin)
echo '<MATRIZ_JSON>' | venv/bin/python3 scripts/cpc_image_gen.py \
  --mode <0|1|2> \
  --width <ancho> \
  --height <alto> \
  --colors "<id1,id2,...>" \
  --output-dir <ruta_proyecto>

# Ejemplo modo 1, imagen 32×32, 4 colores
echo '[[0,0,...]]' | venv/bin/python3 scripts/cpc_image_gen.py \
  --mode 1 --width 32 --height 32 \
  --colors "0,9,18,26" \
  --output-dir /Users/destroyer/PROJECTS/CPCReady/cpcready-skills
```

El script devuelve JSON con la ruta del archivo generado:
```json
{
  "ok": true,
  "file": "/ruta/cpc_1_1743851234.png",
  "mode": 1,
  "width": 32,
  "height": 32,
  "colors": [0, 9, 18, 26],
  "color_names": ["Negro", "Verde", "Verde intenso", "Blanco intenso"]
}
```

### 6. Mostrar el resultado y pedir feedback

Después de generar, muestra un resumen al usuario y **siempre pregunta**:

```
He generado la imagen. Aquí está el resumen:

| Campo    | Valor           |
|----------|-----------------|
| Archivo  | cpc_1_XXXX.png  |
| Modo     | 1 (320×200)     |
| Colores  | 0 (Negro), 9 (Verde), 18 (Verde intenso), 26 (Blanco) |
| Tamaño   | 32×32 píxeles   |

¿Quieres cambiar algo? (colores, tamaño, detalles del diseño, añadir elementos...)
```

### 7. Iterar según el feedback

Si el usuario pide cambios:
- **Colores diferentes**: actualiza la paleta y regenera
- **Más grande/pequeño**: ajusta dimensiones (respetando máximo del modo)
- **Cambios en el diseño**: rediseña la matriz de píxeles
- **Otro modo**: valida que los colores encajen en el nuevo límite

Repite hasta que el usuario apruebe la imagen.

### 8. Guardar el archivo final

El archivo se guarda automáticamente con el formato:
```
cpc_{modo}_{timestamp_unix}.png
```

En la carpeta raíz del proyecto activo. Informa al usuario de la ruta exacta.

---

## Restricciones técnicas — SIEMPRE respetar

| Modo | Resolución máx | Colores simultáneos | Nunca superar |
|------|----------------|---------------------|---------------|
| 0    | 160×200        | 16                  | 160px ancho, 200px alto, 16 colores |
| 1    | 320×200        | 4                   | 320px ancho, 200px alto, 4 colores |
| 2    | 640×200        | 2                   | 640px ancho, 200px alto, 2 colores |

- Los colores deben pertenecer a la paleta oficial de 27 colores CPC (IDs 0-26)
- Los tamaños pueden ser **menores** que el máximo, nunca mayores
- Si el usuario pide más colores de los que permite el modo, sugiere el modo
  con más colores o reduce la paleta al máximo permitido

---

## Estilo visual esperado

Consultar las imágenes de referencia en `/Users/destroyer/Downloads/imagenes-amstrad/`
para entender el estilo esperado. Características clave:

- **Píxeles visibles y cuadrados**: sin anti-aliasing, sin suavizado
- **Contornos definidos**: normalmente en negro (color 0) o color muy oscuro
- **Gradientes por tramado**: para simular más tonos con pocos colores,
  alterna píxeles de dos colores vecinos
- **Proporciones de la época**: personajes altos y estilizados, proporciones
  ligeramente exageradas como en los juegos del CPC
- **Fondos simples**: rellenos planos o degradados básicos para ahorrar colores
  para los elementos principales

---

## Comandos de utilidad del script

```bash
# Listar los 27 colores disponibles con sus IDs y valores RGB
venv/bin/python3 scripts/cpc_image_gen.py --list-colors

# Listar modos de pantalla disponibles
venv/bin/python3 scripts/cpc_image_gen.py --list-modes
```

---

## Recursos

- `scripts/cpc_image_gen.py`: Generador de imágenes PNG (Pillow + numpy)
- `references/cpc-colors.md`: Paleta completa + combinaciones recomendadas
- `venv/`: Entorno virtual Python con Pillow y numpy instalados
- `/Users/destroyer/Downloads/imagenes-amstrad/`: Imágenes de referencia de estilo

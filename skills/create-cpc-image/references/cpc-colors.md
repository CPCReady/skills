# Referencia de Colores y Modos — Amstrad CPC

## Modos gráficos

El Amstrad CPC ofrece tres modos de pantalla. La resolución y los colores
simultáneos son las dos restricciones fundamentales que deben respetarse siempre.

| Modo | Resolución | Colores simultáneos | Bits/píxel | Uso típico |
|------|------------|---------------------|------------|------------|
| 0    | 160×200    | 16 de 27            | 4 bits     | Personajes detallados, escenas ricas en color |
| 1    | 320×200    | 4 de 27             | 2 bits     | Juegos, sprites, equilibrio detalle/color |
| 2    | 640×200    | 2 de 27             | 1 bit      | Texto, gráficos monocromos, máximo detalle H |

> **Regla clave**: los colores simultáneos son los que pueden aparecer en
> pantalla al mismo tiempo. El artista elige cuáles N colores de los 27
> disponibles activa para esa imagen.

---

## Paleta completa — 27 colores

| ID | Nombre           | Hex       | RGB               |
|----|------------------|-----------|-------------------|
| 0  | Negro            | `#000000` | 0, 0, 0           |
| 1  | Azul             | `#000080` | 0, 0, 128         |
| 2  | Azul intenso     | `#0000FF` | 0, 0, 255         |
| 3  | Rojo             | `#800000` | 128, 0, 0         |
| 4  | Magenta          | `#800080` | 128, 0, 128       |
| 5  | Malva            | `#8000FF` | 128, 0, 255       |
| 6  | Rojo intenso     | `#FF0000` | 255, 0, 0         |
| 7  | Morado           | `#FF0080` | 255, 0, 128       |
| 8  | Magenta intenso  | `#FF00FF` | 255, 0, 255       |
| 9  | Verde            | `#008000` | 0, 128, 0         |
| 10 | Cyan             | `#008080` | 0, 128, 128       |
| 11 | Azul celeste     | `#0080FF` | 0, 128, 255       |
| 12 | Amarillo         | `#808000` | 128, 128, 0       |
| 13 | Blanco           | `#808080` | 128, 128, 128     |
| 14 | Azul pastel      | `#8080FF` | 128, 128, 255     |
| 15 | Anaranjado       | `#FF8000` | 255, 128, 0       |
| 16 | Rosado           | `#FF8080` | 255, 128, 128     |
| 17 | Magenta pastel   | `#FF80FF` | 255, 128, 255     |
| 18 | Verde intenso    | `#00FF00` | 0, 255, 0         |
| 19 | Verde mar        | `#00FF80` | 0, 255, 128       |
| 20 | Cyan intenso     | `#00FFFF` | 0, 255, 255       |
| 21 | Verde lima       | `#80FF00` | 128, 255, 0       |
| 22 | Verde pastel     | `#80FF80` | 128, 255, 128     |
| 23 | Cyan pastel      | `#80FFFF` | 128, 255, 255     |
| 24 | Amarillo intenso | `#FFFF00` | 255, 255, 0       |
| 25 | Amarillo pastel  | `#FFFF80` | 255, 255, 128     |
| 26 | Blanco intenso   | `#FFFFFF` | 255, 255, 255     |

---

## Combinaciones de colores recomendadas por modo

### Modo 1 (4 colores) — Combinaciones clásicas

| Escenario            | Colores (IDs)     | Descripción                             |
|----------------------|-------------------|-----------------------------------------|
| Personaje día        | 0, 26, 15, 9      | Negro, blanco, naranja, verde           |
| Personaje noche      | 0, 1, 13, 26      | Negro, azul, gris, blanco               |
| Fantasma/zombie      | 0, 13, 26, 18     | Negro, gris, blanco, verde intenso      |
| Guerrero/héroe       | 0, 3, 15, 26      | Negro, rojo oscuro, naranja, blanco     |
| Naturaleza/exterior  | 0, 9, 18, 26      | Negro, verde, verde intenso, blanco     |
| Agua/océano          | 0, 1, 11, 20      | Negro, azul, celeste, cyan              |

### Modo 0 (16 colores) — Mayor libertad artística

Con 16 colores simultáneos, la paleta puede incluir toda la gama tonal
necesaria para un personaje completo:
- **Sombras**: colores 0, 1, 3, 4 (oscuros)
- **Medios tonos**: colores 9, 10, 12, 13 (medios)
- **Luces**: colores 18, 20, 24, 26 (claros)
- **Acentos**: cualquier color vibrante restante

### Modo 2 (2 colores) — Alto contraste

Solo se pueden usar 2 colores. Combinaciones habituales:
- `0, 26` — Negro sobre blanco (texto, siluetas)
- `0, 18` — Negro sobre verde (pantalla fosforescente)
- `0, 24` — Negro sobre amarillo intenso (advertencia)

---

## Notas sobre el pixel art CPC auténtico

- Los juegos de la época usaban píxeles rectangulares en pantalla real
  (los monitores CPC distorsionaban ligeramente la imagen)
- El pixel art moderno para CPC mantiene resoluciones nativas pero se
  visualiza en monitores cuadrados
- Los sprites de personajes típicos medían entre 16×24 y 32×48 píxeles
- Las pantallas de juego completas usaban la resolución máxima del modo
- Se reservaban colores específicos para el fondo (PAPER) y los sprites (PEN)

---

## Referencias de imágenes de ejemplo

Las imágenes en `/Users/destroyer/Downloads/imagenes-amstrad/` muestran
el estilo visual esperado:

| Archivo          | Descripción                      |
|------------------|----------------------------------|
| `hobbit.jpg`     | Personaje tipo RPG, vista lateral |
| `aceps*.jpg`     | Secuencia de personaje en acción |
| `zombi1.jpg`     | Personaje monstruo/zombie        |
| `don*.jpg`       | Personaje aventurero             |
| `vera*.jpg`      | Personaje femenino               |
| `h*.jpg`         | Fondos/escenarios                |

Usar como referencia de **estilo**, no de paleta (son fotografías de pantalla
y pueden contener más colores de los que permite el modo CPC).

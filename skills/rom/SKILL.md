---
name: rom
description: Crear y gestionar imágenes ROM (.cpr) para consolas Amstrad GX-4000 a partir de discos DSK. Usar cuando el usuario pida operar imágenes CPR con nocart (create, dumpdsk, check), cuando necesite convertir herramientas en DSK a formato cartucho o hacer dump a imágenes ROM. Herramienta Python multiplataforma.
---

# rom

## Flujo recomendado

1. Verificar que Python 3 esté disponible en el sistema.
2. Ejecutar directamente `nocart.py` desde `scripts/` (no requiere instalación ni entorno virtual).
3. La salida por defecto es JSON para facilitar el parseo automático que debes hacer como agente IA. Siempre debes formatear esta salida como Markdown antes de presentarla al usuario (ej. tablas para comandos check o listas de atributos para create).
4. **Para la creación de ROMs:** NUNCA asumas comandos `--command` o nombres de ficheros inventados. Deja que `nocart.py` interactivamente pida el nombre de los discos de entrada y salida, al igual que la acción a efectuar.

## Herramienta Python pura

Esta skill incluye una herramienta Python autocontenida en `scripts/nocart.py`.

**No requiere instalación**: ejecuta directamente con Python 3:

```bash
python3 scripts/nocart.py <action> [input_file] [output_file] [options]
```

Requisitos:
- Python 3.6+
- Solo usa bibliotecas estándar

## Comandos disponibles

Sintaxis principal con los siguientes subcomandos/acciones:

```bash
nocart.py create <input_dsk> <output_cpr> [--command "str"]
nocart.py dumpdsk <input_dsk> <output_bin>
nocart.py check <input_cpr>
```

### Comando: create

Crea un archivo de cartucho .cpr válido para la GX-4000 o emuladores partiendo de una imagen de disco DSK.

```bash
nocart.py create game.dsk game.cpr --command 'run"disc"'
```

Opciones:
- `--command <cmd>`: Comando BASIC que correrá al insertar el cartucho. Máximo 16 caracteres.

### Comando: dumpdsk

Vuelca/Extrae todo el contenido de un fichero .dsk, como si ya estuviera escrito en un fichero .cpr para parchear su contenido directamente.

```bash
nocart.py dumpdsk disk.dsk dump.bin
```

### Comando: check

Valida si un fichero .cpr dado tiene la estructura de metadatos correcta RIFF+AMS!, verificando un correcto formateo de chunk IDs.

```bash
nocart.py check game.cpr
```

## Salida de Información

El comportamiento del script te devolverá siempre un JSON como este:

```json
{
  "status": "ok",
  "action": "check",
  "input_file": "game.cpr",
  "header": {
    "tag": "RIFF",
    "size": 131206,
    "type": "AMS!"
  },
  "chunks": [
    {
       "index": 0,
       "offset_hex": "0x12",
       "tag": "cb00",
       "size": 16384
    }
  ],
  "logs": []
}
```

**Como agente inteligente estás OBLIGADO a:**
- Nunca mostrar JSON crudo al usuario.
- Parsear en memoria la respuesta de `status` a `"ok"` o `"error"`.
- Formatear una tabla markdown elegante si se ha efectuado el `check` iterando por `chunks`.

## Prompts interactivos

`nocart.py` incluye validaciones automáticas. Si lo ejecutas en TTY y omitiste argumentos como la acción o el fichero de origen y destino, saltará un bucle de preguntas hasta que el usuario introduzca los datos necesarios (o hasta recibir parámetros válidos).

- Si estás operando de fondo o usando `run_command` como un agente, y sabes qué parámetros pasar (por que el usuario te lo ha dicho en el chat), inclúyelos siempre por CLI `args`. No inventes si faltan, invoca interactivamente sin args.

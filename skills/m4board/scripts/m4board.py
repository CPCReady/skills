#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
M4Board Tool - Control remoto de tarjeta M4 para Amstrad CPC.
"""

import requests
import os
import sys
import json
import argparse
from pathlib import Path

# Estructura JSON de salida
json_out = {
    "status": "ok",
    "action": None,
    "ip": None,
    "data": {}
}

class M4BoardException(Exception):
    pass

class M4Board(object):
    def __init__(self, ip):
        self._ip = ip

    def _get_url(self, path):
        return f"http://{self._ip}/{path}"
    
    def _get_headers(self):
        return {"user-agent": "m4board-cpc"}

    def _upload_file(self, path, destination, opt):
        if not os.path.isfile(path):
            raise M4BoardException(f"El archivo {path} no existe o no es válido.")

        if opt != 0:
            raise M4BoardException("Se requiere añadir una cabecera AMSDOS, no soportado por ahora.")

        url = self._get_url("upload.html")
        r = requests.post(
            url,
            files={"upfile" : (
                    destination + "/" + os.path.basename(path),
                    open(path, 'rb'),
                    "Content-Type: application/octet-stream",
                    {'Expires': '0'}
                )}
        )
        if r.status_code != 200:
            raise M4BoardException(f"Upload falló con status HTTP {r.status_code}")
        
        json_out["data"]["uploaded_file"] = path
        json_out["data"]["destination"] = destination

    def _upload_dir(self, path, destination, opt):
        if not os.path.isdir(path):
            raise M4BoardException(f"El directorio {path} no existe.")

        removed_base = path[:-len(os.path.basename(path))]
        uploaded = []

        def _treat_dir(current_dir):
            current_base = (destination + "/" + current_dir[len(removed_base):]).replace("//", "/").replace(' ', '_')

            self.mkdir(current_base)
            for filename in os.listdir(current_dir):
                full_filename = os.path.join(path, filename)
                self.upload(full_filename, current_base, opt)
                uploaded.append(full_filename)

        _treat_dir(path)
        json_out["data"]["uploaded_files"] = uploaded

    def reset_m4(self):
        url = self._get_url("config.cgi?mres")
        r = requests.get(url, headers=self._get_headers())
        if r.status_code != 200:
            raise M4BoardException("Reset M4 falló.")
        json_out["data"]["message"] = "M4 reseteada con éxito."

    def reset_cpc(self):
        url = self._get_url("config.cgi?cres")
        r = requests.get(url, headers=self._get_headers())
        if r.status_code != 200:
            raise M4BoardException("Reset CPC falló.")
        json_out["data"]["message"] = "CPC reseteado con éxito."

    def upload(self, path, destination, opt):
        if not os.path.exists(path):
            raise M4BoardException(f"El archivo/directorio {path} no existe.")

        if os.path.isdir(path):
            self._upload_dir(path, destination, opt)
        else:
            self._upload_file(path, destination, opt)

    def download(self, path, opt):
        url = self._get_url(f"sd/{path}")
        r = requests.get(url)
        if r.status_code != 200:
            raise M4BoardException(f"No se pudo descargar {path}.")

        local_name = os.path.basename(path)
        with open(local_name, 'wb') as f:
            f.write(r.content)
            
        json_out["data"]["downloaded_file"] = local_name
        json_out["data"]["size"] = len(r.content)

    def execute(self, cpcfile):
        url = self._get_url("config.cgi")
        r = requests.get(url, params={"run2": cpcfile})
        if r.status_code != 200:
            raise M4BoardException(f"Ejecución de {cpcfile} falló.")
        json_out["data"]["executed"] = cpcfile

    def mkdir(self, folder):
        if folder[0] != "/":
            folder = "/" + folder

        url = self._get_url("config.cgi")
        r = requests.get(url, params={"mkdir": folder}, headers=self._get_headers())
        if r.status_code != 200:
            raise M4BoardException(f"Creación de directorio {folder} falló.")
        json_out["data"]["directory_created"] = folder

    def cd(self, cpcfolder):
        url = self._get_url("config.cgi")
        r = requests.get(url, params={"cd": cpcfolder})
        if r.status_code != 200:
            raise M4BoardException(f"Cambio de directorio a {cpcfolder} falló.")
        json_out["data"]["new_directory"] = cpcfolder

    def rm(self, cpcfile):
        url = self._get_url("config.cgi")
        r = requests.get(url, params={"rm": cpcfile})
        if r.status_code != 200:
            raise M4BoardException(f"Eliminado de {cpcfile} falló.")
        json_out["data"]["removed"] = cpcfile

    def del_rom(self, romid):
        if not (0 <= int(romid) <= 31):
            raise M4BoardException("ROM ID debe estar entre 0 y 31.")
        url = self._get_url("roms.shtml")
        r = requests.get(url, params={"rmsl": romid})
        if r.status_code != 200:
            raise M4BoardException(f"Borrado de ROM {romid} falló.")
        json_out["data"]["deleted_rom_id"] = romid

    def put_rom(self, fname, romid, name):
        if not (0 <= int(romid) <= 31):
            raise M4BoardException("ROM ID debe estar entre 0 y 31.")
        if not os.path.isfile(fname):
            raise M4BoardException(f"Archivo ROM {fname} no encontrado.")

        url = self._get_url("roms.shtml")
        r = requests.post(
            url,
            data={"slotnum": romid, "slotname": name},
            files={
                "uploadedfile": (
                    "rom.bin",
                    open(fname, 'rb'),
                    "Content-Type: application/octet-stream",
                    {'Expires': '0'}               
                )
            }
        )
        if r.status_code != 200:
            raise M4BoardException(f"Puesta de ROM {fname} en ranura {romid} falló.")
        
        json_out["data"]["rom_installed"] = {"file": fname, "slot": romid, "name": name}

    def pause(self):
        url = self._get_url("config.cgi")
        r = requests.get(url, params={"chlt": "CPC+Pause"})
        if r.status_code != 200:
            raise M4BoardException("Imposible pausar CPC.")
        json_out["data"]["message"] = "CPC pausado."

    def ls(self, cpcfolder):
        url = self._get_url("config.cgi")
        r = requests.get(url, params={"ls": cpcfolder})
        if r.status_code != 200:
            raise M4BoardException("Fallo al inicializar listado.")

        url_list = self._get_url("sd/m4/dir.txt")
        r_list = requests.get(url_list)
        if r_list.status_code != 200:
            raise M4BoardException("Fallo al obtener el archivo dir.txt de la tarjeta.")
        
        json_out["data"]["directory"] = cpcfolder
        json_out["data"]["listing"] = r_list.text


def interactive_fallback():
    if not sys.stdin.isatty():
        return
        
    print("### Modo interactivo m4board", file=sys.stderr)

    ip = os.environ.get('M4BOARD_IP', '')
    if not ip:
        while not ip:
            print("\nIntroduce la IP de la tarjeta M4 (ej. 192.168.1.15): ", file=sys.stderr, end='')
            ip = input().strip()
            if ip:
                os.environ['M4BOARD_IP'] = ip

    actions = [
        "reset_cpc", "reboot_m4", "upload", "download", 
        "execute", "run", "mkdir", "cd", "rm", "delrom", "putrom", "pause", "ls"
    ]
    
    action = None
    while action not in actions:
        print(f"\nAcción a realizar ({'/'.join(actions)}): ", file=sys.stderr, end='')
        action = input().strip().lower()
        
    # Build dynamic argv insertion
    sys.argv.insert(1, action)
    
    if action == "ls":
        print("\nDirectorio a listar (pulsa enter para vacío): ", file=sys.stderr, end='')
        folder = input().strip()
        if folder:
             sys.argv.append(folder)
             
    elif action in ["upload"]:
             print("\nRuta del archivo a subir: ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             # Destino opcional? Por rapidez, mandaremos a / si no contesta
             print("Ruta de destino en M4 (ej / o /juegos/): ", file=sys.stderr, end='')
             dest = input().strip()
             if dest: sys.argv.append(dest)
             
    elif action in ["download", "execute", "run", "rm"]:
             print("\nArchivo en el M4 a procesar: ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             
    elif action == "mkdir" or action == "cd":
             print("\nRuta del directorio: ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             
    elif action == "delrom":
             print("\nSlot ID del ROM a borrar (0-31): ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             
    elif action == "putrom":
             print("\nRuta del archivo local: ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             print("Slot ID del ROM donde instalar (0-31): ", file=sys.stderr, end='')
             sys.argv.append(input().strip())
             print("Nombre descriptivo para la ROM: ", file=sys.stderr, end='')
             sys.argv.append(input().strip())

def main():
    if sys.stdin.isatty() and len(sys.argv) == 1:
        interactive_fallback()
        
    parser = argparse.ArgumentParser(description="M4Board Python XFER Manager")
    parser.add_argument("--ip", help="IP del M4Board. Alternativa a M4BOARD_IP.")
    
    subparsers = parser.add_subparsers(dest="action", help="Acciones disponibles")
    
    subparsers.add_parser("reset_cpc")
    subparsers.add_parser("reboot_m4")
    
    p_upload = subparsers.add_parser("upload")
    p_upload.add_argument("file", help="Archivo a subir")
    p_upload.add_argument("dest", nargs="?", default="/", help="Directorio destino en la SD del M4")
    
    p_download = subparsers.add_parser("download")
    p_download.add_argument("cpcfile", help="Archivo en la SD a descargar")
    
    p_exec = subparsers.add_parser("execute")
    p_exec.add_argument("cpcfile", help="Archivo a ejecutar en el M4")
    
    p_run = subparsers.add_parser("run")
    p_run.add_argument("file", help="Upload a /tmp y ejecución")
    
    p_mkdir = subparsers.add_parser("mkdir")
    p_mkdir.add_argument("folder", help="Crear directorio")
    
    p_cd = subparsers.add_parser("cd")
    p_cd.add_argument("folder", help="Cambiar directorio actual (cd)")
    
    p_rm = subparsers.add_parser("rm")
    p_rm.add_argument("cpcfile", help="Eliminar fichero del M4")
    
    p_delrom = subparsers.add_parser("delrom")
    p_delrom.add_argument("romid", help="ID del slot ROM a eliminar")
    
    p_putrom = subparsers.add_parser("putrom")
    p_putrom.add_argument("file", help="Archivo ROM")
    p_putrom.add_argument("romid", help="Slot ID (0-31)")
    p_putrom.add_argument("name", help="Nombre descriptivo de la ROM")
    
    subparsers.add_parser("pause")
    
    p_ls = subparsers.add_parser("ls")
    p_ls.add_argument("folder", nargs="?", default="", help="Directorio a listar")

    args = parser.parse_args()
    
    if not args.action:
        sys.stderr.write("Falta acción a realizar.\n")
        sys.exit(1)

    ip = args.ip or os.environ.get('M4BOARD_IP')
    if not ip:
        print(json.dumps({"status": "error", "error": "IP del M4Board no configurada. Usa --ip o la variable M4BOARD_IP."}))
        sys.exit(1)

    json_out["action"] = args.action
    json_out["ip"] = ip
    
    m4 = M4Board(ip)

    try:
        if args.action == "reset_cpc":
            m4.reset_cpc()
        elif args.action == "reboot_m4":
            m4.reset_m4()
        elif args.action == "upload":
            m4.upload(args.file, args.dest, 0)
        elif args.action == "download":
            m4.download(args.cpcfile, 1)
        elif args.action == "execute":
            m4.execute(args.cpcfile)
        elif args.action == "run":
            m4.upload(args.file, "/tmp", 0)
            m4.execute("/tmp/" + os.path.basename(args.file))
        elif args.action == "mkdir":
            m4.mkdir(args.folder)
        elif args.action == "cd":
            m4.cd(args.folder)
        elif args.action == "rm":
            m4.rm(args.cpcfile)
        elif args.action == "delrom":
            m4.del_rom(args.romid)
        elif args.action == "putrom":
            m4.put_rom(args.file, args.romid, args.name)
        elif args.action == "pause":
            m4.pause()
        elif args.action == "ls":
            m4.ls(args.folder)

        print(json.dumps(json_out, indent=2))
        
    except M4BoardException as e:
        print(json.dumps({"status": "error", "error": str(e), "action": args.action}), indent=2)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "critical", "error": f"Internal Error: {str(e)}", "action": args.action}), indent=2)
        sys.exit(1)

if __name__ == '__main__':
    main()

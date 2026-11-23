"""Guardado de la información en un archivo JSON."""

import json
import os

from paqueteria.excepciones import ErrorArchivo


class Almacen:
    """Lee y escribe el archivo con los datos del sistema."""

    def __init__(self, ruta):
        self.ruta = ruta

    def leer(self):
        """Regresa los datos guardados o None si no hay archivo."""
        try:
            with open(self.ruta, encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return None
        except (OSError, ValueError, RecursionError) as error:
            raise ErrorArchivo(f"{self.ruta} está dañado: {error}")

    def guardar(self, datos):
        """Escribe primero en un temporal para no dañar el archivo si algo falla."""
        temporal = self.ruta + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.ruta) or ".", exist_ok=True)
            with open(temporal, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            os.replace(temporal, self.ruta)
        except OSError as error:
            raise ErrorArchivo(f"no se pudo guardar {self.ruta}: {error}")

    def apartar_danado(self):
        """Cambia el nombre del archivo dañado para conservarlo."""
        numero = 1
        while os.path.exists(f"{self.ruta}.danado{numero}"):
            numero += 1
        nuevo = f"{self.ruta}.danado{numero}"
        try:
            os.replace(self.ruta, nuevo)
        except OSError as error:
            raise ErrorArchivo(f"no se pudo apartar {self.ruta}: {error}")
        return nuevo

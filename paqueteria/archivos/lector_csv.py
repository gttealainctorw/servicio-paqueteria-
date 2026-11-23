"""Lectura de archivos CSV."""

import csv

from paqueteria.excepciones import ErrorArchivo


def leer_csv(ruta, columnas):
    """Regresa una lista de (número de renglón, diccionario) con los datos del archivo.

    Lanza ErrorArchivo si el archivo no se puede leer o le faltan columnas.
    """
    try:
        with open(ruta, newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)
            faltan = [c for c in columnas if c not in (lector.fieldnames or [])]
            if faltan:
                raise ErrorArchivo(f"a {ruta} le faltan columnas: {', '.join(faltan)}")
            return [(lector.line_num, fila) for fila in lector]
    except FileNotFoundError:
        raise ErrorArchivo(f"no existe el archivo {ruta}")
    except (OSError, ValueError, csv.Error) as error:
        raise ErrorArchivo(f"no se pudo leer {ruta}: {error}")

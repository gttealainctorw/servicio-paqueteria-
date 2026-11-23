"""Inicio del programa."""

import argparse
import os
import sys

from paqueteria.archivos.almacen import Almacen
from paqueteria.excepciones import ErrorArchivo, ErrorPaqueteria
from paqueteria.menu import Menu
from paqueteria.operacion.central import Central
from paqueteria.operacion.tarifario import Tarifario


def cargar_guardado(central, almacen):
    """Recupera lo guardado. Regresa True si había información."""
    try:
        datos = almacen.leer()
        if datos is None:
            return False
        central.restaurar(datos)
        return True
    except ErrorArchivo as error:
        print(f"Aviso: {error}")
        print(f"Se apartó como {almacen.apartar_danado()} y se empieza sin datos.")
        return False


def main():
    """Lee los argumentos, carga los archivos y abre el menú."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Servicio de paquetería")
    parser.add_argument("--datos", default="datos", help="carpeta con los CSV")
    parser.add_argument("--guardado", default="guardado/sistema.json", help="archivo del sistema")
    parser.add_argument("--reportes", default="reportes", help="carpeta de los reportes")
    args = parser.parse_args()
    try:
        tarifario = Tarifario(os.path.join(args.datos, "tarifas.csv"),
                              os.path.join(args.datos, "zonas.csv"))
        central = Central(tarifario)
        almacen = Almacen(args.guardado)
        if not cargar_guardado(central, almacen):
            for renglon, motivo in central.cargar_repartidores(
                    os.path.join(args.datos, "repartidores.csv")):
                print(f"Repartidor del renglón {renglon} rechazado: {motivo}")
    except ErrorPaqueteria as error:
        print(f"No se puede iniciar: {error}")
        return 1
    Menu(central, almacen, args.reportes).ejecutar()
    return 0


if __name__ == "__main__":
    sys.exit(main())

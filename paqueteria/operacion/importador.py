"""Importación de los envíos de un cliente empresarial."""

from paqueteria.archivos.lector_csv import leer_csv
from paqueteria.excepciones import DatoInvalido, ErrorPaqueteria

COLUMNAS = ["tipo", "servicio", "remitente", "destinatario", "direccion", "cp", "peso",
            "largo", "ancho", "alto", "valor"]


def importar_envios(central, ruta, fecha):
    """Registra los envíos válidos del CSV.

    Regresa dos listas: los envíos registrados y los rechazados como (renglón, motivo).
    """
    registrados = []
    rechazados = []
    for renglon, fila in leer_csv(ruta, COLUMNAS):
        try:
            if None in fila:
                raise DatoInvalido("tiene columnas de más")
            registrados.append(central.registrar(fila, fecha))
        except ErrorPaqueteria as error:
            rechazados.append((renglon, str(error)))
    return registrados, rechazados

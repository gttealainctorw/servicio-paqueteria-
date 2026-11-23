"""Funciones para revisar los datos del usuario y de los archivos."""

import math
from datetime import datetime

from paqueteria.excepciones import DatoInvalido

MAXIMO = 1000000


def leer_texto(valor, nombre):
    """Regresa el texto sin espacios o lanza DatoInvalido si está vacío."""
    texto = str(valor if valor is not None else "").strip()
    if not texto:
        raise DatoInvalido(f"falta {nombre}")
    return texto


def leer_positivo(valor, nombre):
    """Convierte a número y revisa que sea mayor que cero."""
    texto = leer_texto(valor, nombre)
    try:
        numero = float(texto)
    except ValueError:
        raise DatoInvalido(f"{nombre} no es un número: '{texto}'")
    if not math.isfinite(numero) or numero <= 0:
        raise DatoInvalido(f"{nombre} debe ser mayor que cero")
    if numero > MAXIMO:
        raise DatoInvalido(f"{nombre} es demasiado grande")
    return numero


def leer_cp(valor):
    """Revisa que el código postal tenga cinco dígitos."""
    cp = leer_texto(valor, "código postal")
    if len(cp) != 5 or not (cp.isascii() and cp.isdigit()):
        raise DatoInvalido(f"código postal inválido: '{cp}'")
    return cp


def leer_fecha_hora(texto):
    """Convierte 'AAAA-MM-DD HH:MM' a datetime."""
    try:
        return datetime.strptime(texto.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        raise DatoInvalido(f"fecha inválida: '{texto}' (use AAAA-MM-DD HH:MM)")


def leer_dia(texto):
    """Convierte 'AAAA-MM-DD' a date."""
    try:
        return datetime.strptime(texto.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise DatoInvalido(f"día inválido: '{texto}' (use AAAA-MM-DD)")

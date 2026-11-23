"""Servicios de entrega."""

from abc import ABC, abstractmethod
from datetime import timedelta

from paqueteria.excepciones import DatoInvalido


class Servicio(ABC):
    """Cómo cambia el precio y cuánto tarda un envío."""

    nombre = ""

    @abstractmethod
    def aplicar(self, costo):
        """Regresa el costo con este servicio."""

    @abstractmethod
    def fechas_entrega(self, fecha):
        """Regresa la primera y la última fecha estimada."""


class Estandar(Servicio):
    """De 3 a 5 días, sin costo extra."""

    nombre = "estandar"

    def aplicar(self, costo):
        """El costo no cambia."""
        return costo

    def fechas_entrega(self, fecha):
        """De 3 a 5 días después."""
        return (fecha + timedelta(days=3)).date(), (fecha + timedelta(days=5)).date()


class Express(Servicio):
    """Al día siguiente, 50 % más caro."""

    nombre = "express"

    def aplicar(self, costo):
        """Aumenta el costo 50 %."""
        return costo * 1.5

    def fechas_entrega(self, fecha):
        """El día siguiente."""
        manana = (fecha + timedelta(days=1)).date()
        return manana, manana


SERVICIOS = {"estandar": Estandar, "express": Express}


def crear_servicio(nombre):
    """Crea el servicio a partir de su nombre."""
    clave = str(nombre or "").strip().lower().replace("á", "a")
    if clave not in SERVICIOS:
        raise DatoInvalido(f"servicio desconocido: '{nombre or ''}'")
    return SERVICIOS[clave]()

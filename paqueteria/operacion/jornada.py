"""Simulación de una jornada de reparto."""

from paqueteria.excepciones import ErrorPaqueteria

# Espacio de Sebastian


class Jornada:
    """Todos los repartidores recorren sus rutas al mismo tiempo."""

    def __init__(self, central, inicio):
        self.central = central
        self.inicio = inicio

    def simular(self):
        """Corre la jornada mostrando el avance y regresa True si los estados coinciden."""
        raise ErrorPaqueteria("pendiente: simulación de la jornada")

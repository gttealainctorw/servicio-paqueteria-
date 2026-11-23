"""Excepciones propias del sistema."""


class ErrorPaqueteria(Exception):
    """Error base. El menú atrapa esta clase y muestra el mensaje."""


class DatoInvalido(ErrorPaqueteria):
    """Un dato falta, no tiene el formato correcto o está fuera de rango."""


class EnvioNoPermitido(ErrorPaqueteria):
    """El envío no cumple una regla del servicio."""


class CambioNoValido(ErrorPaqueteria):
    """El envío no puede pasar al estado pedido."""


class CapacidadExcedida(ErrorPaqueteria):
    """El envío no cabe en el vehículo del repartidor."""


class NoEncontrado(ErrorPaqueteria):
    """No existe la guía o el repartidor."""


class ErrorArchivo(ErrorPaqueteria):
    """Un archivo no existe, está dañado o no se puede escribir."""

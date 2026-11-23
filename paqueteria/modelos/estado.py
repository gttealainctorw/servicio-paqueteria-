"""Estados de un envío y cambios permitidos."""

from datetime import datetime
from enum import Enum


class Estado(Enum):
    """Estados por los que puede pasar un envío."""

    REGISTRADO = "registrado"
    EN_ALMACEN = "en almacén"
    EN_RUTA = "en ruta"
    ENTREGADO = "entregado"
    DEVUELTO = "devuelto al remitente"
    CANCELADO = "cancelado"


# De EN_RUTA al almacén o a devuelto solo se llega con un intento fallido.
TRANSICIONES = {
    Estado.REGISTRADO: (Estado.EN_ALMACEN, Estado.CANCELADO),
    Estado.EN_ALMACEN: (Estado.EN_RUTA, Estado.CANCELADO),
    Estado.EN_RUTA: (Estado.ENTREGADO,),
    Estado.ENTREGADO: (),
    Estado.DEVUELTO: (),
    Estado.CANCELADO: (),
}


class CambioEstado:
    """Un renglón del historial de un envío."""

    def __init__(self, estado, fecha, nota="", repartidor=""):
        self.estado = estado
        self.fecha = fecha
        self.nota = nota
        self.repartidor = repartidor

    def a_dict(self):
        """Regresa los datos para guardarlos."""
        return {"estado": self.estado.name, "fecha": self.fecha.isoformat(),
                "nota": self.nota, "repartidor": self.repartidor}

    @classmethod
    def desde_dict(cls, datos):
        """Crea el renglón con los datos guardados."""
        return cls(Estado[datos["estado"]], datetime.fromisoformat(datos["fecha"]),
                   datos["nota"], datos["repartidor"])

    def __str__(self):
        texto = f"{self.fecha:%Y-%m-%d %H:%M}  {self.estado.value}"
        if self.nota:
            texto += f" ({self.nota})"
        if self.repartidor:
            texto += f" [{self.repartidor}]"
        return texto

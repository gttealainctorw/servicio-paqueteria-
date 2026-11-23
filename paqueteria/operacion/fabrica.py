"""Creación de envíos según su tipo."""

from paqueteria.excepciones import DatoInvalido
from paqueteria.modelos.envio import Paquete, PaqueteFragil, PaqueteRefrigerado, Sobre
from paqueteria.modelos.servicio import crear_servicio

TIPOS = {clase.tipo: clase for clase in (Sobre, Paquete, PaqueteFragil, PaqueteRefrigerado)}


class FabricaEnvios:
    """Elige la clase que corresponde a cada envío."""

    @staticmethod
    def crear(datos, zona):
        """Crea un envío nuevo con los datos recibidos."""
        tipo = str(datos.get("tipo") or "").strip().lower().replace("á", "a")
        if tipo not in TIPOS:
            raise DatoInvalido(f"tipo de envío desconocido: '{tipo}'")
        return TIPOS[tipo](datos, crear_servicio(datos.get("servicio")), zona)

    @staticmethod
    def restaurar(datos):
        """Crea un envío con los datos guardados."""
        envio = FabricaEnvios.crear(datos, datos["zona"])
        envio.restaurar(datos)
        return envio

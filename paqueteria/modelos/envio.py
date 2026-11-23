"""Tipos de envío."""

from abc import ABC, abstractmethod

from paqueteria.excepciones import CambioNoValido, EnvioNoPermitido
from paqueteria.modelos.estado import TRANSICIONES, CambioEstado, Estado
from paqueteria.validacion import leer_cp, leer_positivo, leer_texto

PESO_MAXIMO_SOBRE = 1
PESO_MAXIMO = 500
MAXIMO_INTENTOS = 3


class Envio(ABC):
    """Datos, precio y estado de un envío."""

    tipo = ""

    def __init__(self, datos, servicio, zona):
        self.remitente = leer_texto(datos.get("remitente"), "remitente")
        self.destinatario = leer_texto(datos.get("destinatario"), "destinatario")
        self.direccion = leer_texto(datos.get("direccion"), "dirección")
        self.cp = leer_cp(datos.get("cp"))
        self.peso = leer_positivo(datos.get("peso"), "peso")
        self.servicio = servicio
        self.zona = zona
        self.guia = ""
        self.costo = 0.0
        self.__historial = []
        self.__intentos = 0

    @property
    def estado(self):
        """Estado actual, o None si todavía no se registra."""
        return self.__historial[-1].estado if self.__historial else None

    @property
    def historial(self):
        """Copia del historial."""
        return list(self.__historial)

    @property
    def intentos(self):
        """Número de intentos fallidos."""
        return self.__intentos

    @property
    def fecha_registro(self):
        """Fecha en que se registró."""
        return self.__historial[0].fecha

    @abstractmethod
    def costo_base(self, tarifa):
        """Costo sin servicio ni seguro."""

    def seguro(self):
        """Costo del seguro."""
        return 0.0

    def validar(self):
        """Revisa las reglas del tipo de envío."""
        if self.peso > PESO_MAXIMO:
            raise EnvioNoPermitido(f"el peso máximo es de {PESO_MAXIMO} kg")

    def cotizar(self, tarifa):
        """Valida el envío y regresa su precio total."""
        self.validar()
        return round(self.servicio.aplicar(self.costo_base(tarifa)) + self.seguro(), 2)

    def registrar(self, guia, costo, fecha):
        """Le pone guía y costo, y abre el historial."""
        self.guia = guia
        self.costo = costo
        self.__historial.append(CambioEstado(Estado.REGISTRADO, fecha))

    def cambiar_estado(self, nuevo, fecha, repartidor=""):
        """Cambia el estado si la transición es válida."""
        if nuevo not in TRANSICIONES[self.estado]:
            raise CambioNoValido(
                f"{self.guia}: no se puede pasar de '{self.estado.value}' a '{nuevo.value}'")
        if nuevo is Estado.CANCELADO and self.__intentos > 0:
            raise CambioNoValido(f"{self.guia}: ya salió a ruta, no se puede cancelar")
        self.__revisar_fecha(fecha)
        self.__historial.append(CambioEstado(nuevo, fecha, "", repartidor))

    def intento_fallido(self, fecha, repartidor=""):
        """Regresa el envío al almacén, o al remitente si es el tercer intento."""
        if self.estado is not Estado.EN_RUTA:
            raise CambioNoValido(f"{self.guia}: solo hay intentos de entrega si está en ruta")
        self.__revisar_fecha(fecha)
        self.__intentos += 1
        nuevo = Estado.DEVUELTO if self.__intentos >= MAXIMO_INTENTOS else Estado.EN_ALMACEN
        nota = f"intento fallido {self.__intentos}"
        self.__historial.append(CambioEstado(nuevo, fecha, nota, repartidor))

    def __revisar_fecha(self, fecha):
        ultima = self.__historial[-1].fecha
        if fecha < ultima:
            raise CambioNoValido(
                f"{self.guia}: la fecha es anterior al último cambio ({ultima:%Y-%m-%d %H:%M})")

    def estado_al(self, dia):
        """Estado al terminar ese día, o None si aún no existía."""
        estado = None
        for cambio in self.__historial:
            if cambio.fecha.date() <= dia:
                estado = cambio.estado
        return estado

    def a_dict(self):
        """Regresa los datos para guardarlos."""
        return {"tipo": self.tipo, "servicio": self.servicio.nombre, "zona": self.zona,
                "remitente": self.remitente, "destinatario": self.destinatario,
                "direccion": self.direccion, "cp": self.cp, "peso": self.peso,
                "guia": self.guia, "costo": self.costo, "intentos": self.__intentos,
                "historial": [cambio.a_dict() for cambio in self.__historial]}

    def restaurar(self, datos):
        """Recupera guía, costo e historial guardados."""
        self.guia = leer_texto(datos["guia"], "guía")
        self.costo = float(datos["costo"])
        self.__intentos = int(datos["intentos"])
        self.__historial = [CambioEstado.desde_dict(d) for d in datos["historial"]]
        if not self.__historial:
            raise ValueError("historial vacío")


class Sobre(Envio):
    """Sobre con tarifa fija por zona."""

    tipo = "sobre"

    def validar(self):
        """Un sobre no pesa más de 1 kg."""
        if self.peso > PESO_MAXIMO_SOBRE:
            raise EnvioNoPermitido(f"un sobre no puede pesar más de {PESO_MAXIMO_SOBRE} kg")

    def costo_base(self, tarifa):
        """Tarifa fija."""
        return tarifa.sobre


class Paquete(Envio):
    """Paquete que se cobra por kilogramo."""

    tipo = "paquete"

    def __init__(self, datos, servicio, zona):
        super().__init__(datos, servicio, zona)
        self.largo = leer_positivo(datos.get("largo"), "largo")
        self.ancho = leer_positivo(datos.get("ancho"), "ancho")
        self.alto = leer_positivo(datos.get("alto"), "alto")

    @property
    def peso_cobrado(self):
        """El mayor entre el peso real y el volumétrico."""
        return max(self.peso, self.largo * self.ancho * self.alto / 5000)

    def costo_base(self, tarifa):
        """Peso cobrado por la tarifa de la zona."""
        return self.peso_cobrado * tarifa.kilo

    def a_dict(self):
        """Agrega las medidas."""
        datos = super().a_dict()
        datos.update(largo=self.largo, ancho=self.ancho, alto=self.alto)
        return datos


class PaqueteFragil(Paquete):
    """Paquete con 20 % adicional y seguro obligatorio."""

    tipo = "fragil"

    def __init__(self, datos, servicio, zona):
        super().__init__(datos, servicio, zona)
        self.valor = leer_positivo(datos.get("valor"), "valor declarado")

    def costo_base(self, tarifa):
        """Costo de paquete más 20 %."""
        return super().costo_base(tarifa) * 1.20

    def seguro(self):
        """3 % del valor declarado."""
        return self.valor * 0.03

    def a_dict(self):
        """Agrega el valor declarado."""
        datos = super().a_dict()
        datos["valor"] = self.valor
        return datos


class PaqueteRefrigerado(Paquete):
    """Paquete que solo viaja por express y no va a zona nacional."""

    tipo = "refrigerado"

    def validar(self):
        """Revisa el servicio y la zona."""
        super().validar()
        if self.servicio.nombre != "express":
            raise EnvioNoPermitido("un refrigerado solo se envía por express")
        if self.zona == "nacional":
            raise EnvioNoPermitido("un refrigerado no se envía a zona nacional")

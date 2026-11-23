"""Repartidores y sus vehículos."""

from paqueteria.excepciones import CapacidadExcedida, DatoInvalido
from paqueteria.validacion import leer_texto


class Vehiculo:
    """Vehículo con una capacidad en kilogramos."""

    nombre = ""
    capacidad = 0


class Motocicleta(Vehiculo):
    """Carga hasta 20 kg."""

    nombre = "motocicleta"
    capacidad = 20


class Camioneta(Vehiculo):
    """Carga hasta 500 kg."""

    nombre = "camioneta"
    capacidad = 500


VEHICULOS = {"motocicleta": Motocicleta, "camioneta": Camioneta}


class Repartidor:
    """Persona que entrega los envíos que se le asignan."""

    def __init__(self, clave, nombre, vehiculo):
        self.clave = leer_texto(clave, "clave").upper()
        self.nombre = leer_texto(nombre, "nombre")
        tipo = leer_texto(vehiculo, "vehículo").lower()
        if tipo not in VEHICULOS:
            raise DatoInvalido(f"vehículo desconocido: '{vehiculo}'")
        self.vehiculo = VEHICULOS[tipo]()
        self.__envios = []

    @property
    def envios(self):
        """Copia de los envíos asignados."""
        return list(self.__envios)

    @property
    def carga(self):
        """Kilogramos asignados."""
        return round(sum(envio.peso for envio in self.__envios), 6)

    def puede_cargar(self, envio):
        """Indica si el envío cabe en su vehículo."""
        return round(self.carga + envio.peso, 6) <= self.vehiculo.capacidad

    def asignar(self, envio):
        """Agrega el envío si no excede la capacidad."""
        if not self.puede_cargar(envio):
            libre = self.vehiculo.capacidad - self.carga
            raise CapacidadExcedida(
                f"{envio.guia} pesa {envio.peso:g} kg y a {self.nombre} le quedan {libre:g} kg")
        self.__envios.append(envio)

    def quitar(self, envio):
        """Quita el envío de su carga."""
        self.__envios.remove(envio)

    def a_dict(self):
        """Regresa los datos para guardarlos."""
        return {"clave": self.clave, "nombre": self.nombre, "vehiculo": self.vehiculo.nombre,
                "guias": [envio.guia for envio in self.__envios]}

    def __str__(self):
        return (f"{self.clave} {self.nombre} - {self.vehiculo.nombre}: {len(self.__envios)} envíos, "
                f"{self.carga:g}/{self.vehiculo.capacidad} kg")

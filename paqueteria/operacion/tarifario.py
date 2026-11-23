"""Zonas y tarifas."""

from paqueteria.archivos.lector_csv import leer_csv
from paqueteria.excepciones import DatoInvalido, EnvioNoPermitido, ErrorArchivo
from paqueteria.validacion import leer_cp, leer_positivo, leer_texto

ZONAS = ("local", "regional", "nacional")


class Tarifa:
    """Precios de una zona."""

    def __init__(self, sobre, kilo):
        self.sobre = leer_positivo(sobre, "tarifa de sobre")
        self.kilo = leer_positivo(kilo, "tarifa por kilo")


class Tarifario:
    """Busca la zona de un código postal y su tarifa."""

    def __init__(self, ruta_tarifas, ruta_zonas):
        self.__tarifas = {}
        self.__rangos = []
        self.__cargar_tarifas(ruta_tarifas)
        self.__cargar_zonas(ruta_zonas)

    def __cargar_tarifas(self, ruta):
        for renglon, fila in leer_csv(ruta, ["zona", "sobre", "kilo"]):
            try:
                zona = self.__leer_zona(fila["zona"])
                if zona in self.__tarifas:
                    raise DatoInvalido(f"zona repetida: '{zona}'")
                self.__tarifas[zona] = Tarifa(fila["sobre"], fila["kilo"])
            except DatoInvalido as error:
                raise ErrorArchivo(f"{ruta}, renglón {renglon}: {error}")
        faltan = [z for z in ZONAS if z not in self.__tarifas]
        if faltan:
            raise ErrorArchivo(f"a {ruta} le faltan zonas: {', '.join(faltan)}")

    def __cargar_zonas(self, ruta):
        for renglon, fila in leer_csv(ruta, ["desde", "hasta", "zona"]):
            try:
                self.__rangos.append((leer_cp(fila["desde"]), leer_cp(fila["hasta"]),
                                      self.__leer_zona(fila["zona"])))
            except DatoInvalido as error:
                raise ErrorArchivo(f"{ruta}, renglón {renglon}: {error}")

    def __leer_zona(self, valor):
        zona = leer_texto(valor, "zona").lower()
        if zona not in ZONAS:
            raise DatoInvalido(f"zona desconocida: '{zona}'")
        return zona

    def zona(self, cp):
        """Zona del primer rango que contiene el código postal."""
        for desde, hasta, zona in self.__rangos:
            if desde <= cp <= hasta:
                return zona
        raise EnvioNoPermitido(f"no hay servicio al código postal {cp}")

    def tarifa(self, zona):
        """Tarifa de una zona."""
        return self.__tarifas[zona]

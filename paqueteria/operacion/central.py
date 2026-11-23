"""Central de la empresa: reúne las operaciones del sistema."""

import functools
import threading

from paqueteria.archivos.lector_csv import leer_csv
from paqueteria.excepciones import (CambioNoValido, DatoInvalido, ErrorArchivo, ErrorPaqueteria,
                                    NoEncontrado)
from paqueteria.modelos.estado import Estado
from paqueteria.modelos.repartidor import Repartidor
from paqueteria.operacion.fabrica import FabricaEnvios
from paqueteria.validacion import leer_cp


def sincronizado(metodo):
    """Decorador: solo un hilo a la vez puede ejecutar el método."""
    @functools.wraps(metodo)
    def wrapper(self, *args, **kwargs):
        with self._candado:
            return metodo(self, *args, **kwargs)
    return wrapper


class Central:
    """Administra los envíos y los repartidores."""

    def __init__(self, tarifario):
        self._candado = threading.RLock()
        self.__tarifario = tarifario
        self.__envios = {}
        self.__repartidores = {}
        self.__ultima_guia = 0

    @property
    @sincronizado
    def envios(self):
        """Lista de envíos."""
        return list(self.__envios.values())

    @property
    @sincronizado
    def repartidores(self):
        """Lista de repartidores."""
        return list(self.__repartidores.values())

    def cotizar(self, datos):
        """Regresa el envío (sin registrar) y su precio."""
        zona = self.__tarifario.zona(leer_cp(datos.get("cp")))
        envio = FabricaEnvios.crear(datos, zona)
        return envio, envio.cotizar(self.__tarifario.tarifa(zona))

    @sincronizado
    def registrar(self, datos, fecha):
        """Cotiza, asigna una guía y guarda el envío."""
        envio, costo = self.cotizar(datos)
        self.__ultima_guia += 1
        envio.registrar(f"PQ{self.__ultima_guia:06d}", costo, fecha)
        self.__envios[envio.guia] = envio
        return envio

    @sincronizado
    def buscar(self, guia):
        """Busca un envío por su guía."""
        clave = guia.strip().upper()
        if clave not in self.__envios:
            raise NoEncontrado(f"no existe la guía '{clave}'")
        return self.__envios[clave]

    @sincronizado
    def buscar_repartidor(self, clave):
        """Busca un repartidor por su clave."""
        clave = clave.strip().upper()
        if clave not in self.__repartidores:
            raise NoEncontrado(f"no existe el repartidor '{clave}'")
        return self.__repartidores[clave]

    @sincronizado
    def repartidor_de(self, envio):
        """Repartidor que tiene asignado el envío, o None."""
        for repartidor in self.__repartidores.values():
            if envio in repartidor.envios:
                return repartidor
        return None

    @sincronizado
    def agregar_repartidor(self, clave, nombre, vehiculo):
        """Da de alta un repartidor."""
        repartidor = Repartidor(clave, nombre, vehiculo)
        if repartidor.clave in self.__repartidores:
            raise DatoInvalido(f"ya existe el repartidor {repartidor.clave}")
        self.__repartidores[repartidor.clave] = repartidor
        return repartidor

    def cargar_repartidores(self, ruta):
        """Da de alta los repartidores de un CSV y regresa los rechazados."""
        rechazados = []
        for renglon, fila in leer_csv(ruta, ["clave", "nombre", "vehiculo"]):
            try:
                self.agregar_repartidor(fila["clave"], fila["nombre"], fila["vehiculo"])
            except ErrorPaqueteria as error:
                rechazados.append((renglon, str(error)))
        return rechazados

    @sincronizado
    def por_asignar(self):
        """Envíos en el almacén que no tienen repartidor."""
        return [e for e in self.__envios.values()
                if e.estado is Estado.EN_ALMACEN and self.repartidor_de(e) is None]

    @sincronizado
    def asignar(self, guia, clave):
        """Asigna un envío del almacén a un repartidor."""
        envio = self.buscar(guia)
        repartidor = self.buscar_repartidor(clave)
        if envio.estado is not Estado.EN_ALMACEN:
            raise CambioNoValido(f"{envio.guia} no está en el almacén")
        if self.repartidor_de(envio) is not None:
            raise CambioNoValido(f"{envio.guia} ya tiene repartidor")
        repartidor.asignar(envio)
        return repartidor

    @sincronizado
    def cambiar_estado(self, guia, nuevo, fecha):
        """Cambia el estado de un envío. Para salir a ruta debe tener repartidor."""
        envio = self.buscar(guia)
        repartidor = self.repartidor_de(envio)
        if nuevo is Estado.EN_RUTA and envio.estado is Estado.EN_ALMACEN and repartidor is None:
            raise CambioNoValido(f"{envio.guia} no tiene repartidor asignado")
        envio.cambiar_estado(nuevo, fecha, repartidor.clave if repartidor else "")
        if repartidor and nuevo in (Estado.ENTREGADO, Estado.CANCELADO):
            repartidor.quitar(envio)
        return envio

    @sincronizado
    def intento_fallido(self, guia, fecha):
        """Registra que no se pudo entregar el envío."""
        envio = self.buscar(guia)
        repartidor = self.repartidor_de(envio)
        envio.intento_fallido(fecha, repartidor.clave if repartidor else "")
        if repartidor:
            repartidor.quitar(envio)
        return envio

    @sincronizado
    def a_dict(self):
        """Regresa todos los datos para guardarlos."""
        return {"ultima_guia": self.__ultima_guia,
                "envios": [e.a_dict() for e in self.__envios.values()],
                "repartidores": [r.a_dict() for r in self.__repartidores.values()]}

    @sincronizado
    def restaurar(self, datos):
        """Recupera los datos guardados. Si algo está mal no cambia nada."""
        try:
            envios = {}
            for guardado in datos["envios"]:
                envio = FabricaEnvios.restaurar(guardado)
                envios[envio.guia] = envio
            repartidores = {}
            for guardado in datos["repartidores"]:
                repartidor = Repartidor(guardado["clave"], guardado["nombre"], guardado["vehiculo"])
                for guia in guardado["guias"]:
                    repartidor.asignar(envios[guia])
                repartidores[repartidor.clave] = repartidor
            ultima = max([int(datos["ultima_guia"])] + [int(guia[2:]) for guia in envios])
        except (ErrorPaqueteria, KeyError, TypeError, ValueError, AttributeError,
                OverflowError) as error:
            raise ErrorArchivo(f"los datos guardados no son válidos: {error}")
        self.__envios = envios
        self.__repartidores = repartidores
        self.__ultima_guia = ultima

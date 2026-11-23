"""Simulación de una jornada de reparto."""

import random
import threading
import time
from datetime import timedelta

from paqueteria.excepciones import CambioNoValido, ErrorPaqueteria
from paqueteria.modelos.envio import MAXIMO_INTENTOS
from paqueteria.modelos.estado import Estado

PROBABILIDAD_FALLA = 0.10


class Ruta(threading.Thread):
    """Hilo con el recorrido de un repartidor."""

    def __init__(self, central, repartidor, inicio):
        super().__init__(daemon=True)
        self.central = central
        self.repartidor = repartidor
        self.hora = inicio
        self.envios = repartidor.envios
        self.hechos = 0
        self.resultados = {}
        self.error = ""

    def run(self):
        """Saca los envíos a ruta y trata de entregar cada uno."""
        try:
            for envio in self.envios:
                if envio.estado is Estado.EN_ALMACEN:
                    self.central.cambiar_estado(envio.guia, Estado.EN_RUTA, self.hora)
            for envio in self.envios:
                time.sleep(random.uniform(0.2, 0.8))
                self.hora += timedelta(minutes=random.randint(10, 30))
                self.__entregar(envio)
                self.hechos += 1
        except ErrorPaqueteria as error:
            self.error = str(error)

    def __entregar(self, envio):
        if random.random() < PROBABILIDAD_FALLA:
            ultimo = envio.intentos + 1 >= MAXIMO_INTENTOS
            self.central.intento_fallido(envio.guia, self.hora)
            self.resultados[envio.guia] = Estado.DEVUELTO if ultimo else Estado.EN_ALMACEN
        else:
            self.central.cambiar_estado(envio.guia, Estado.ENTREGADO, self.hora)
            self.resultados[envio.guia] = Estado.ENTREGADO

    def avance(self):
        """Texto con lo que lleva."""
        return f"{self.repartidor.clave}: {self.hechos} de {len(self.envios)}"


class Jornada:
    """Todos los repartidores recorren sus rutas al mismo tiempo."""

    def __init__(self, central, inicio):
        self.central = central
        self.inicio = inicio
        self.rutas = []

    def simular(self):
        """Corre la jornada mostrando el avance y regresa True si los estados coinciden."""
        self.rutas = [Ruta(self.central, r, self.inicio)
                      for r in self.central.repartidores if r.envios]
        self.__revisar()
        for ruta in self.rutas:
            ruta.start()
        try:
            while any(ruta.is_alive() for ruta in self.rutas):
                self.__mostrar()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Terminando las entregas que faltan...")
        for ruta in self.rutas:
            ruta.join()
        self.__mostrar()
        return self.verificar()

    def __revisar(self):
        if not self.rutas:
            raise CambioNoValido("no hay envíos asignados a los repartidores")
        for ruta in self.rutas:
            for envio in ruta.envios:
                if envio.historial[-1].fecha > self.inicio:
                    raise CambioNoValido(
                        f"la jornada empieza antes del último cambio de {envio.guia}")

    def __mostrar(self):
        print(" | ".join(ruta.avance() for ruta in self.rutas))

    def verificar(self):
        """Compara lo que anotó cada hilo con el estado de los envíos."""
        correcta = True
        for ruta in self.rutas:
            if ruta.error:
                print(f"{ruta.repartidor.clave} no terminó: {ruta.error}")
                correcta = False
            for envio in ruta.envios:
                if envio.estado is not ruta.resultados.get(envio.guia):
                    print(f"{envio.guia} no coincide")
                    correcta = False
        total = sum(len(ruta.resultados) for ruta in self.rutas)
        entregados = sum(estado is Estado.ENTREGADO
                         for ruta in self.rutas for estado in ruta.resultados.values())
        print(f"{entregados} entregados, {total - entregados} intentos fallidos")
        return correcta

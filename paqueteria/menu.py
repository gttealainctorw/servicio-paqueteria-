"""Menú de texto."""

from datetime import datetime

from paqueteria.excepciones import DatoInvalido, ErrorPaqueteria
from paqueteria.modelos.estado import Estado
from paqueteria.operacion.asignacion import asignar_todos
from paqueteria.operacion.fabrica import TIPOS
from paqueteria.operacion.importador import importar_envios
from paqueteria.operacion.jornada import Jornada
from paqueteria.operacion.reporte import generar_reporte
from paqueteria.validacion import leer_dia, leer_fecha_hora


class Menu:
    """Muestra las opciones y llama a la central."""

    def __init__(self, central, almacen, carpeta_reportes):
        self.central = central
        self.almacen = almacen
        self.carpeta_reportes = carpeta_reportes
        self.opciones = [
            ("Cotizar envío", self.cotizar),
            ("Registrar envío", self.registrar),
            ("Rastrear guía", self.rastrear),
            ("Cambiar estado", self.cambiar_estado),
            ("Asignar un envío", self.asignar),
            ("Asignar todos los envíos del almacén", self.asignar_todos),
            ("Importar envíos desde CSV", self.importar),
            ("Reporte de un día", self.reporte),
            ("Simular jornada de reparto", self.simular),
            ("Ver envíos", self.ver_envios),
            ("Ver repartidores", self.ver_repartidores),
            ("Agregar repartidor", self.agregar_repartidor),
            ("Recibir en almacén todos los registrados", self.recibir_todos),
        ]

    def ejecutar(self):
        """Repite el menú hasta que el usuario sale."""
        while True:
            try:
                print("\n--- Servicio de paquetería ---")
                for numero, (texto, _) in enumerate(self.opciones, 1):
                    print(f"{numero:2}. {texto}")
                print(" 0. Salir")
                opcion = input("Opción: ").strip()
                if opcion == "0":
                    print("Hasta luego.")
                    return
                self.__llamar(opcion)
            except ErrorPaqueteria as error:
                print(f"Error: {error}")
            except UnicodeDecodeError:
                print("Error: se escribió un carácter que no se puede leer")
            except (EOFError, KeyboardInterrupt):
                print("\nHasta luego.")
                return

    def __llamar(self, opcion):
        if opcion not in [str(n) for n in range(1, len(self.opciones) + 1)]:
            raise DatoInvalido("opción no válida")
        self.opciones[int(opcion) - 1][1]()

    def __guardar(self):
        self.almacen.guardar(self.central.a_dict())

    def __pedir_fecha(self):
        texto = input("Fecha y hora AAAA-MM-DD HH:MM (Enter = ahora): ")
        if not texto.strip():
            return datetime.now().replace(microsecond=0)
        return leer_fecha_hora(texto)

    def __pedir_envio(self):
        datos = {"tipo": input(f"Tipo ({', '.join(TIPOS)}): ").strip().lower()}
        if datos["tipo"] not in TIPOS:
            raise DatoInvalido(f"tipo de envío desconocido: '{datos['tipo']}'")
        campos = ["servicio", "remitente", "destinatario", "direccion", "cp", "peso"]
        if datos["tipo"] != "sobre":
            campos += ["largo", "ancho", "alto"]
        if datos["tipo"] == "fragil":
            campos.append("valor")
        textos = {"servicio": "Servicio (estandar, express)", "direccion": "Dirección",
                  "cp": "Código postal", "peso": "Peso (kg)", "largo": "Largo (cm)",
                  "ancho": "Ancho (cm)", "alto": "Alto (cm)", "valor": "Valor declarado"}
        for campo in campos:
            datos[campo] = input(f"{textos.get(campo, campo.capitalize())}: ")
        return datos

    def __mostrar_precio(self, envio, costo, fecha):
        primera, ultima = envio.servicio.fechas_entrega(fecha)
        print(f"Zona {envio.zona}, costo ${costo:.2f}")
        if primera == ultima:
            print(f"Entrega estimada: {primera}")
        else:
            print(f"Entrega estimada: del {primera} al {ultima}")

    def cotizar(self):
        """Muestra el precio de un envío sin registrarlo."""
        envio, costo = self.central.cotizar(self.__pedir_envio())
        self.__mostrar_precio(envio, costo, self.__pedir_fecha())

    def registrar(self):
        """Registra un envío."""
        datos = self.__pedir_envio()
        fecha = self.__pedir_fecha()
        envio = self.central.registrar(datos, fecha)
        self.__guardar()
        print(f"Envío registrado con la guía {envio.guia}")
        self.__mostrar_precio(envio, envio.costo, fecha)

    def rastrear(self):
        """Muestra el estado y el historial de una guía."""
        envio = self.central.buscar(input("Guía: "))
        print(f"{envio.guia}: {envio.estado.value}")
        for cambio in envio.historial:
            print(f"  {cambio}")

    def cambiar_estado(self):
        """Cambia el estado de un envío."""
        guia = input("Guía: ")
        print("1 en almacén, 2 en ruta, 3 entregado, 4 intento fallido, 5 cancelado")
        estados = {"1": Estado.EN_ALMACEN, "2": Estado.EN_RUTA, "3": Estado.ENTREGADO,
                   "5": Estado.CANCELADO}
        opcion = input("Nuevo estado: ").strip()
        if opcion != "4" and opcion not in estados:
            raise DatoInvalido("estado no válido")
        fecha = self.__pedir_fecha()
        if opcion == "4":
            envio = self.central.intento_fallido(guia, fecha)
        else:
            envio = self.central.cambiar_estado(guia, estados[opcion], fecha)
        self.__guardar()
        print(f"{envio.guia}: {envio.estado.value}")

    def asignar(self):
        """Asigna un envío a un repartidor."""
        guia = input("Guía: ")
        repartidor = self.central.asignar(guia, input("Clave del repartidor: "))
        self.__guardar()
        print(f"Asignado a {repartidor}")

    def asignar_todos(self):
        """Reparte los envíos del almacén."""
        asignados, sin_lugar = asignar_todos(self.central)
        self.__guardar()
        for guia, clave in asignados:
            print(f"{guia} -> {clave}")
        for guia in sin_lugar:
            print(f"{guia} no cupo en ningún vehículo")
        print(f"{len(asignados)} asignados, {len(sin_lugar)} sin lugar")

    def importar(self):
        """Importa los envíos de un cliente empresarial."""
        ruta = input("Archivo CSV: ").strip()
        registrados, rechazados = importar_envios(self.central, ruta, self.__pedir_fecha())
        self.__guardar()
        for envio in registrados:
            print(f"{envio.guia} {envio.tipo} ${envio.costo:.2f}")
        for renglon, motivo in rechazados:
            print(f"Renglón {renglon} rechazado: {motivo}")
        print(f"{len(registrados)} registrados, {len(rechazados)} rechazados")

    def reporte(self):
        """Genera el reporte de un día."""
        dia = leer_dia(input("Día AAAA-MM-DD: "))
        print(f"Reporte guardado en {generar_reporte(self.central, dia, self.carpeta_reportes)}")

    def simular(self):
        """Simula una jornada de reparto."""
        correcta = Jornada(self.central, self.__pedir_fecha()).simular()
        self.__guardar()
        print("Los estados coinciden" if correcta else "Hay estados que no coinciden")

    def ver_envios(self):
        """Lista los envíos."""
        for envio in self.central.envios:
            print(f"{envio.guia} {envio.tipo} {envio.servicio.nombre} {envio.zona} "
                  f"{envio.peso:g} kg ${envio.costo:.2f} - {envio.estado.value}")
        print(f"{len(self.central.envios)} envíos")

    def ver_repartidores(self):
        """Lista los repartidores."""
        for repartidor in self.central.repartidores:
            print(repartidor)

    def agregar_repartidor(self):
        """Da de alta un repartidor."""
        repartidor = self.central.agregar_repartidor(
            input("Clave: "), input("Nombre: "), input("Vehículo (motocicleta, camioneta): "))
        self.__guardar()
        print(f"Agregado: {repartidor}")

    def recibir_todos(self):
        """Pasa al almacén los envíos registrados."""
        recibidos = self.central.recibir_todos(self.__pedir_fecha())
        self.__guardar()
        print(f"{recibidos} envíos en el almacén")

"""Reporte de un día."""

import os

from paqueteria.excepciones import ErrorArchivo
from paqueteria.modelos.estado import Estado
from paqueteria.modelos.servicio import SERVICIOS
from paqueteria.operacion.fabrica import TIPOS


def contar_estados(central, dia):
    """Número de envíos en cada estado al terminar el día."""
    conteo = {estado: 0 for estado in Estado}
    for envio in central.envios:
        estado = envio.estado_al(dia)
        if estado is not None:
            conteo[estado] += 1
    return conteo


def sumar_ingresos(central, dia):
    """Ingresos por tipo y por servicio de los envíos registrados ese día."""
    por_tipo = {tipo: 0.0 for tipo in TIPOS}
    por_servicio = {servicio: 0.0 for servicio in SERVICIOS}
    for envio in central.envios:
        if envio.fecha_registro.date() != dia or envio.estado_al(dia) is Estado.CANCELADO:
            continue
        por_tipo[envio.tipo] += envio.costo
        por_servicio[envio.servicio.nombre] += envio.costo
    return por_tipo, por_servicio


def contar_entregas(central, dia):
    """Entregas que hizo cada repartidor ese día."""
    entregas = {repartidor.clave: 0 for repartidor in central.repartidores}
    for envio in central.envios:
        for cambio in envio.historial:
            if cambio.estado is Estado.ENTREGADO and cambio.fecha.date() == dia:
                entregas[cambio.repartidor] = entregas.get(cambio.repartidor, 0) + 1
    return entregas


def generar_reporte(central, dia, carpeta):
    """Escribe el reporte del día en un archivo de texto y regresa su ruta."""
    por_tipo, por_servicio = sumar_ingresos(central, dia)
    lineas = [f"Reporte del {dia}", "", "Envíos por estado"]
    for estado, total in contar_estados(central, dia).items():
        lineas.append(f"  {estado.value}: {total}")
    for titulo, ingresos in (("tipo de envío", por_tipo), ("servicio", por_servicio)):
        lineas += ["", f"Ingresos por {titulo}"]
        for nombre, monto in ingresos.items():
            lineas.append(f"  {nombre}: ${monto:.2f}")
        lineas.append(f"  total: ${sum(ingresos.values()):.2f}")
    lineas += ["", "Entregas por repartidor"]
    nombres = {r.clave: r.nombre for r in central.repartidores}
    for clave, total in contar_entregas(central, dia).items():
        lineas.append(f"  {clave} {nombres.get(clave, '')}: {total}")
    ruta = os.path.join(carpeta, f"reporte_{dia}.txt")
    try:
        os.makedirs(carpeta, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(lineas) + "\n")
    except OSError as error:
        raise ErrorArchivo(f"no se pudo escribir {ruta}: {error}")
    return ruta

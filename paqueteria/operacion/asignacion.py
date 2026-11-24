"""Asignación automática de los envíos del almacén."""


def asignar_todos(central):
    """Reparte los envíos del almacén sin exceder la capacidad de los vehículos.

    Regresa dos listas: los asignados como (guía, clave del repartidor) y las guías que no cupieron.
    """
    asignados = []
    sin_lugar = []
    pendientes = sorted(central.por_asignar(),
                        key=lambda e: (e.servicio.nombre != "express", e.fecha_registro))
    for envio in pendientes:
        posibles = [r for r in central.repartidores if r.puede_cargar(envio)]
        if not posibles:
            sin_lugar.append(envio.guia)
            continue
        elegido = min(posibles, key=lambda r: len(r.envios))
        central.asignar(envio.guia, elegido.clave)
        asignados.append((envio.guia, elegido.clave))
    return asignados, sin_lugar

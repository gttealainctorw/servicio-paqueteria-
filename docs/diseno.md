# Documento de diseño

## 1. Diagramas UML

### Diagrama de clases

![Diagrama de clases](uml/clases.png)

Muestra las clases, sus atributos, sus métodos y cómo se relacionan. Se eligió porque es donde se ve qué hace cada
parte del sistema.

### Diagrama de estados

![Diagrama de estados](uml/estados.png)

Muestra por qué estados pasa un envío. Se eligió porque la mayoría de los rechazos dependen del estado.

### Diagrama de secuencia

![Diagrama de secuencia](uml/secuencia.png)

Muestra la jornada de reparto: un hilo por repartidor y la revisión final. Se eligió porque es la parte donde
varias cosas pasan al mismo tiempo.

## 2. Decisiones de diseño

| Concepto | Dónde se usa | Qué problema resuelve |
|---|---|---|
| Encapsulamiento | Historial e intentos de `Envio`, envíos de `Repartidor` | El estado y la carga solo cambian con métodos que revisan las reglas |
| Herencia y clases abstractas | `Envio` y sus tipos, `Servicio`, `Vehiculo` | Cada tipo solo define lo que lo hace distinto |
| Composición y agregación | `Envio` tiene su historial; `Repartidor` agrupa envíos | El historial no existe sin el envío; el envío sí existe sin repartidor |
| Polimorfismo | `costo_base`, `seguro`, `validar`, `aplicar` | La central cotiza sin preguntar el tipo de envío |
| Excepciones | `excepciones.py` | El menú atrapa un solo error base y muestra el motivo |
| Archivos | `leer_csv`, `Almacen`, `reporte.py` | Cargar tarifas, importar envíos, hacer reportes y conservar los datos; se escribe en un temporal para no dañar lo guardado |
| Hilos | `Ruta` y candado de `Central` | Los repartidores trabajan al mismo tiempo sin dañar los datos |
| Patrones de diseño | `FabricaEnvios` (Factory), `Servicio` (Strategy), `Envio.cotizar` (Template Method), `Central` (Facade) | Crear el tipo correcto, cambiar el precio según el servicio y que el menú use una sola clase |

### Detalles que decidimos

- El 50 % de express se aplica al costo y al 20 % de frágil, pero no al seguro.
- Los días de entrega son naturales.
- Un sobre pesa máximo 1 kg y un paquete 500 kg, que es lo que carga una camioneta.
- La capacidad se revisa con el peso real.
- La zona es la del primer rango de `zonas.csv` que contiene el código postal. El origen es la Ciudad de México.
- Un envío necesita repartidor para salir a ruta. Si la entrega falla, se queda sin repartidor.
- Un envío que ya salió a ruta no se cancela aunque haya regresado al almacén.
- Un cambio no puede tener una fecha anterior al último cambio del envío.
- En la asignación automática van primero los express y después los más antiguos. Cada envío se le da al repartidor
  con menos envíos que todavía lo pueda cargar.
- Los ingresos del reporte son de los envíos registrados ese día, sin los cancelados ese mismo día.
- En la jornada cada intento tiene 10 % de probabilidad de fallar y se hace un intento por envío al día.
- Al importar, si el archivo no tiene las columnas completas no se registra ninguno.
- Se agregó una opción para recibir en el almacén todos los envíos registrados.

## 3. Alternativas

- **Estados con un diccionario o con una clase por estado.** Se eligió el diccionario porque los estados casi no
  tienen comportamiento propio y así las reglas se leen en un solo lugar.
- **JSON o CSV para guardar.** Se eligió JSON porque el historial es una lista dentro de cada envío y en CSV
  harían falta varios archivos relacionados.

## 4. Uso de IA

- Qué se pidió: a partir del enunciado, el código base, los datos de ejemplo, y los diagramas.
- Qué se usó: la primera versión de los módulos de `modelos`, `archivos`, `central`, `tarifario`, `fabrica`,
  `menu` y `main`, y también de `importador`, `asignacion`, `reporte` y `jornada`.
- Qué se corrigió: Con ayuda de la IA se quitó código sobrante, se hizo abstracta la clase Vehiculo y se agregaron las excepciones al diagrama de clases.
- Cómo se verificó: se ejecutaron los casos del README, incluidos los rechazos y los archivos dañados, y se
  repitió la jornada varias veces revisando los estados y la carga.

## 5. Contribuciones

Módulos que subió cada integrante. El origen de la primera versión está en «Uso de IA».

- Martínez Aguilar Carlos Alain:
  - paqueteria/modelos/:
    envio.py (Envio y sus cuatro tipos), servicio.py (Estandar y Express), estado.py (estados, cambios permitidos
    e historial) y repartidor.py (Repartidor y sus vehículos).
  - paqueteria/archivos/:
    lector_csv.py (lectura de CSV) y almacen.py (guardado en JSON).
  - paqueteria/operacion/tarifario.py y fabrica.py:
    zonas y tarifas, y creación de cada tipo de envío.
  - paqueteria/main.py, excepciones.py y validacion.py:
    inicio del programa, errores propios y revisión de datos.
  - datos/:
    tarifas, zonas, repartidores y los archivos con errores de cada uno.
  - paqueteria/operacion/central.py:
        clase Central, que funciona como fachada (Facade) del sistema.
        Tiene los métodos para cotizar, registrar, buscar envíos y repartidores, asignar, cambiar estado,
        registrar intentos fallidos y recibir en almacén todos los envíos registrados.
        Valida que un envío tenga repartidor para salir a ruta.
        Carga repartidores desde CSV.
        Convierte los datos a diccionario para guardarlos (a_dict) y los recupera (restaurar), sin cambiar
        nada si los datos están dañados. Tiene el decorador sincronizado y el candado RLock para que los hilos no dañen los datos.
  - paqueteria/menu.py:
    clase Menu. Las 13 opciones del menú de texto.
    Captura de datos del envío, de la fecha y de los estados.
    Guardado automático después de cada operación.
    Manejo de errores con un solo ErrorPaqueteria, además de EOFError, KeyboardInterrupt y UnicodeDecodeError.
  - README.md:
    instalación, opciones de inicio, guía paso a paso para probar cada función (con los rechazos
    esperados) y estructura del proyecto. docs/diseno.md y diseno.tex: documento de diseño con la
    descripción de los diagramas UML, las decisiones de diseño, las alternativas y la sección de uso de IA.
    Diagramas UML de clases y de estados.
    
- Gonzalez Morales Daniel Alejandro:
  - paqueteria/operacion/importador.py:
    función importar_envios. Lee el CSV de un cliente empresarial con leer_csv y la lista de columnas esperadas (tipo, servicio, remitente,
    destinatario, direccion, cp, peso, largo, ancho, alto, valor). Registra cada renglón válido mediante Central.registrar.
    Rechaza renglones con columnas de más o con datos inválidos, y guarda el número de renglón y el motivo.
    Regresa dos listas: los envíos registrados y los rechazados.
    Si el archivo no tiene las columnas completas o no existe, no se registra ningún envío.
    
  - datos/:
    envios_empresa.csv, envios_errores.csv y envios_sin_columnas.csv.

- Garces Diaz Gustavo Osei:
  - paqueteria/operacion/asignacion.py:
      función asignar_todos. Reparte automáticamente los envíos del almacén que no tienen repartidor.
      Ordena primero los express y después los más antiguos. Da cada envío al repartidor con menos envíos que todavía pueda cargarlo, sin pasar
      la capacidad del vehículo. Regresa los asignados y las guías que no cupieron.
    
  - paqueteria/operacion/reporte.py: reporte de un día.
      Cuenta los envíos por estado al terminar el día (contar_estados).
      Suma los ingresos por tipo y por servicio de los envíos registrados ese día, sin los cancelados el mismo día (sumar_ingresos).
      Cuenta las entregas por repartidor (contar_entregas).
      generar_reporte escribe el resultado en reportes/reporte_AAAA-MM-DD.txt y maneja los errores de escritura.
    
- Garcia Bizueto Sebastian:
  - paqueteria/operacion/jornada.py:
      simulación de una jornada de reparto con hilos. La clase Ruta (threading.Thread) es un hilo por repartidor. Saca sus envíos a ruta y los
      entrega uno por uno con pausas y horas aleatorias. Cada intento tiene 10 % de probabilidad de fallar (PROBABILIDAD_FALLA), y el tercer fallo
      devuelve el envío al remitente. La clase Jornada crea y arranca los hilos, muestra el avance mientras haya hilos vivos, espera con join()
      y permite interrumpir con Ctrl+C sin perder las entregas. Verifica que la jornada no empiece antes del último cambio de cada envío.
      verificar() compara lo que anotó cada hilo con el estado real de los envíos y regresa True o False.
  - docs/uml/:
      diagrama de secuencia.

# Servicio de paquetería

Proyecto final, Tema 3.

Integrantes:

- Martínez Aguilar Carlos Alain
- Gonzalez Morales Daniel Alejandro
- Garces Diaz Gustavo Osei
- Garcia Bizueto Sebastian

## Instalación

Se necesita Python 3.9 o superior. No usa paquetes externos.

```
git clone https://github.com/gttealainctorw/servicio-paqueteria.git
cd servicio-paqueteria
python -m paqueteria.main
```

En Linux o macOS puede ser `python3`. El programa se ejecuta desde la carpeta del proyecto.

Opciones al iniciar: `--datos carpeta`, `--guardado archivo` y `--reportes carpeta`.
Para empezar de cero se borra la carpeta `guardado`.

## Cómo probar cada función

Las pruebas van en orden y empiezan sin datos guardados. Cada línea es lo que se escribe en el menú.
Cuando se pide la fecha se puede dejar vacía para usar la hora actual.

### 1. Cotizar y registrar

- Cotizar: `1`, `sobre`, `express`, `Ana`, `Luis`, `Calle 1`, `97000`, `0.2`, `2026-11-23 09:00`.
  Resultado: zona nacional, $195.00, entrega 2026-11-24.
- Registrar: `2`, `paquete`, `estandar`, `Ana`, `Luis`, `Calle 1`, `50000`, `2`, `50`, `40`, `30`,
  `2026-11-23 09:00`. Resultado: guía PQ000001, $480.00 (se cobran 12 kg volumétricos).
- Registrar: `2`, `fragil`, `express`, `Ana`, `Luis`, `Calle 1`, `04510`, `3`, `10`, `10`, `10`, `1000`,
  `2026-11-23 09:00`. Resultado: guía PQ000002, $165.00.
- Registrar: `2`, `paquete`, `estandar`, `Ana`, `Luis`, `Calle 1`, `01000`, `25`, `10`, `10`, `10`,
  `2026-11-23 09:00`. Resultado: guía PQ000003, $625.00.

Se rechazan:

- Refrigerado estándar: `2`, `refrigerado`, `estandar`, `Ana`, `Luis`, `Calle 1`, `04510`, `4`, `30`, `30`, `30`,
  `2026-11-23 09:00`.
- Refrigerado a zona nacional: igual, con `express` y código postal `97000`.
- Peso negativo, código postal `99` o un sobre de 2 kg.

### 2. Rastrear

- `3`, `PQ000001`.
- Se rechaza: `3`, `PQ999999`.

### 3. Cambiar estado

- Se rechaza: `4`, `PQ000001`, `3`, `2026-11-23 10:00` (no puede pasar de registrado a entregado).
- Al almacén: `4`, `PQ000001`, `1`, `2026-11-23 10:00`. Repetir con `PQ000003`.
- Se rechaza: `4`, `PQ000001`, `2`, `2026-11-23 11:00` (no tiene repartidor).
- Cancelar: `4`, `PQ000002`, `5`, `2026-11-23 10:00`.

### 4. Asignar

- Uno: `5`, `PQ000001`, `R1`. Después puede salir a ruta: `4`, `PQ000001`, `2`, `2026-11-23 11:00`.
- Intento fallido: `4`, `PQ000001`, `4`, `2026-11-23 12:00`. El envío regresa al almacén.
- Se rechaza: `4`, `PQ000001`, `5`, `2026-11-23 13:00` (ya salió a ruta, no se cancela).
- Se rechaza: `5`, `PQ000003`, `R1` (25 kg no caben en una motocicleta).
- Todos: `6`. Asigna PQ000001 y PQ000003 sin pasar la capacidad.

### 5. Importar

- Válidos: `7`, `datos/envios_empresa.csv`, `2026-11-23 14:00`. Registra 20.
- Con errores: `7`, `datos/envios_errores.csv`, `2026-11-23 14:00`. Registra 2 y rechaza 13 con su motivo.
- Se rechaza: `7`, `datos/envios_sin_columnas.csv`, `2026-11-23 14:00`.
- Se rechaza: `7`, `no_existe.csv`, `2026-11-23 14:00`.

### 6. Reporte

- `8`, `2026-11-23`. Se guarda en `reportes/reporte_2026-11-23.txt`.
- Se rechaza: `8`, `2026-13-01`.

### 7. Datos guardados

- Salir con `0`, volver a entrar y usar `10` y `11`: siguen los envíos y los repartidores.
- Archivo dañado: copiar `datos/sistema_danado.json` a `guardado/sistema.json` y abrir el programa. Avisa, aparta
  el archivo y empieza sin datos.
- Tarifas con error: `python -m paqueteria.main --datos datos/tarifas_malas`.
- Repartidores con error: `python -m paqueteria.main --datos datos/repartidores_malos --guardado guardado/otro.json`.

### 8. Simular jornada

Después de importar:

- Recibir todos: `13`, `2026-11-23 18:00`.
- Asignar todos: `6`.
- Se rechaza: `9`, `2026-11-23 08:00` (antes del último cambio de los envíos).
- Simular: `9`, `2026-11-24 08:00`. Muestra el avance y al final dice si los estados coinciden.
- Ver las entregas: `8`, `2026-11-24`.
- Los fallidos regresan al almacén: se pueden asignar con `6` y simular otro día.

## Estructura

- `datos/`: archivos de ejemplo. Las carpetas con `_malas` o `_malos` tienen errores.
- `docs/`: documento de diseño y diagramas.
- `paqueteria/`: código.
  - `main.py`: inicio del programa.
  - `menu.py`: menú de texto.
  - `excepciones.py` y `validacion.py`: errores propios y revisión de datos.
  - `modelos/`: envíos, servicios, estados y repartidores.
  - `operacion/`: tarifas, central, fábrica, importación, asignación, reporte y jornada.
  - `archivos/`: lectura de CSV y guardado en JSON.

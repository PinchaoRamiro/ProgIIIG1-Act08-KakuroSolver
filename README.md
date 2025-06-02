# Reto Final - Programación III

**Grupo 1**
**Universidad Tecnológica de Pereira**
**Programa: Ingeniería de Sistemas y Computación**

**Presentado por:**
- Kenneth Santiago Rodríguez Ramírez
- Ramiro Antonio Pinchao Chachinoy
- Brayan Suárez Ceballos

## Descripción

Este proyecto es un solucionador de Kakuro, un juego de lógica similar al Sudoku pero basado en sumas. El programa carga un tablero desde un archivo de texto, detecta las restricciones y utiliza un algoritmo de backtracking con forward checking para resolver el tablero.

## Formato del Tablero

Cada línea en el archivo representa una celda en el tablero, leída de izquierda a derecha y de arriba a abajo.

- **Celda negra:** Se ingresa un `0`.
- **Celda con restricciones de suma:** Se ingresa con el formato `suma_vertical|suma_horizontal`.
  - Si una suma no tiene valor, se representa con un `0`.
  - Ejemplos: `0|17` (solo suma horizontal), `43|0` (solo suma vertical).
- **Celda jugable (blanca):** Se ingresa un `#`.

## Requisitos

- Python 3.x
- Archivos de tablero en el formato especificado.

## Instalación

1. Clona este repositorio en tu máquina local.
2. Asegúrate de tener Python instalado.
3. Coloca los archivos de tablero en el directorio adecuado.

## Uso

1. Ejecuta el script principal `kakuro_solver.py`.
2. Asegúrate de que los archivos de tablero estén en la ruta correcta y en el formato especificado.

```bash
python kakuro_solver.py

``` 

## Ejemplo de Ejecución

📋 Tablero original:
■ 0|17 0|24 0|30 ■ 0|23 0|16 0|16 ■
# # # # # # # # #
...

✅ Solución encontrada:
■ 0|17 0|24 0|30 ■ 0|23 0|16 0|16 ■
1 2 3 4 5 6 7 8 9
...

🕒 Tiempo: 0.45 segundos

## Notas

* Se garantizan resultados siempre y cuando se cumpla el formato mencionado.
* Los tableros deben provenir de Sudokumania y ser de formato clásico desde la dificultad Fácil a Muy Difícil.
* Maneja correctamente el path del archivo para asegurar que se cargue el tablero adecuado.

## Licencia

Este proyecto es para fines educativos y no tiene licencia específica.
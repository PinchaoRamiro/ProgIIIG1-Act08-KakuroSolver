"""
Reto Final - Programación III
Grupo 1
Universidad Tecnologica de Pereira
Programa: Ingenieria De Sistemas Y Computacion
Presentado por:
                - Kenneth Santiago Rodriguez Ramirez
                - Ramiro Antonio Pinchao Chachinoy
                - Brayan Suarez Ceballos

Salvedad: El formato de los archivos de tablero es el siguiente:
            Cada línea en el archivo representa una celda en el tablero, leída de izquierda a derecha y de arriba a abajo.

            * Para una celda negra: se ingresa un "0".

            * Para una celda con restricciones de suma: se ingresa con el formato "suma_vertical|suma_horizontal".
                * Si una suma no tiene valor, se representa con un "0".
                * Ejemplos: "0|17" (solo suma horizontal), "43|0" (solo suma vertical).

            * Para una celda jugable (blanca): se ingresa un "#".



          Se garantizan resultados siempre y cuando se cumpla el formato mencionado, el sudoku provenga de https://www.sudokumania.com.ar/kakuro/
          siendo kakuros de formato clasico desde la dificultad Fácil a Muy difícil y se maneje correctamente el path del archivo.
"""


import itertools
import time

# ----------- Celdas del tablero -----------
class Celda:
    """
    Clase base para representar una celda genérica en el tablero de Kakuro.
    Almacena el valor asignado y el dominio de valores posibles.
    """
    def __init__(self, value=None, domain=None):
        """
        Inicializa una celda.
        Args:
            value (int, optional): El valor numérico de la celda. None si está vacía.
            domain (set, optional): El conjunto de valores posibles para la celda (1-9 por defecto).
        """
        self.value = value
        self.domain = domain or set(range(1, 10))

    def __str__(self):
        """
        Retorna la representación en cadena de la celda.
        Muestra el valor si está asignado, o '#' si está vacía.
        """
        return str(self.value) if self.value else "#"

class CeldaNegra(Celda):
    """
    Representa una celda negra en el tablero de Kakuro, que no puede contener un número.
    """
    def __init__(self):
        """
        Inicializa una celda negra. No tiene valor ni dominio de valores.
        """
        super().__init__(None, None)

    def __str__(self):
        """
        Retorna la representación en cadena de la celda negra como un cuadrado sólido.
        """
        return "■"

class CeldaConRestriccion(Celda):
    """
    Representa una celda que contiene las sumas objetivo para las corridas horizontales y/o verticales.
    """
    def __init__(self, sum_vertical=0, sum_horizontal=0):
        """
        Inicializa una celda con restricciones de suma.
        Args:
            sum_vertical (int, optional): La suma objetivo para la corrida vertical debajo de esta celda.
            sum_horizontal (int, optional): La suma objetivo para la corrida horizontal a la derecha de esta celda.
        """
        super().__init__(None, None)
        self.sum_vertical = sum_vertical
        self.sum_horizontal = sum_horizontal

    def __str__(self):
        """
        Retorna la representación en cadena de la celda de restricción, mostrando sus sumas.
        Formato: "Vertical|Horizontal".
        """
        return f"{self.sum_vertical}\\{self.sum_horizontal}".ljust(5)

class CeldaNormal(Celda):
    """
    Representa una celda blanca en el tablero donde se debe colocar un número (1-9).
    """
    def __init__(self):
        """
        Inicializa una celda normal. Su valor inicial es None y su dominio es {1, ..., 9}.
        """
        super().__init__()

# -- Utilities --

COLUMNS = "ABCDEFGHI"
comb_cache = {}

def generate_keys():
    """
    Genera una lista de claves de celdas para un tablero de 9x9 (ej. "A1", "B2").

    Returns:
        list: Una lista de cadenas, cada una representando una clave de celda.
    """
    return [f"{col}{row}" for row, col in itertools.product(range(1, 10), COLUMNS)]

def initialize_board(keys):
    """
    Inicializa un tablero de Kakuro vacío con todas las celdas como CeldaNormal.

    Args:
        keys (list): Una lista de claves de celdas (ej. ["A1", "B1", ...]).

    Returns:
        dict: Un diccionario que mapea cada clave de celda a un objeto CeldaNormal.
    """
    return {key: CeldaNormal() for key in keys}

def load_board(file_path, board):
    """
    Carga la configuración de un tablero de Kakuro desde un archivo de texto.
    Modifica el objeto 'board' para reflejar la configuración del archivo.

    Args:
        file_path (str): La ruta al archivo de texto que contiene la configuración del tablero.
        board (dict): El diccionario del tablero a modificar.
    """
    with open(file_path, 'r') as file:
        for key in board:
            value = file.readline().strip()
            if value == "0":
                board[key] = CeldaNegra()
            elif "|" in value:
                v, h = map(int, value.split("|"))
                board[key] = CeldaConRestriccion(v, h)
            elif value == "#":
                board[key] = CeldaNormal()

def print_board(board):
    """
    Imprime el estado actual del tablero de Kakuro en la consola.

    Args:
        board (dict): El diccionario del tablero a imprimir.
    """
    for row in range(1, 10):
        for col in COLUMNS:
            key = f"{col}{row}"
            print(str(board[key]).ljust(10), end=" ")
        print()

# -- Group detection --

def detect_groups(board):
    """
    Detecta y extrae todos los grupos (corridas) de celdas blancas asociadas a sumas.
    Estos grupos son las restricciones clave en un Kakuro.

    Args:
        board (dict): El diccionario del tablero actual.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un grupo
              con su tipo ("horizontal"/"vertical"), la suma objetivo y las claves de las celdas que lo componen.
    """
    col_idx = {col: idx for idx, col in enumerate(COLUMNS)}
    groups = []

    for key, celda in board.items():
        if isinstance(celda, CeldaConRestriccion):
            col, row = key[0], int(key[1])

            # Detectar grupo horizontal
            if celda.sum_horizontal > 0:
                cells = []
                c = col_idx[col] + 1
                while c < len(COLUMNS):
                    next_cell = f"{COLUMNS[c]}{row}"
                    if isinstance(board.get(next_cell), CeldaNormal):
                        cells.append(next_cell)
                        c += 1
                    else:
                        break
                groups.append({"type": "horizontal", "sum": celda.sum_horizontal, "cells": cells})

            # Detectar grupo vertical
            if celda.sum_vertical > 0:
                cells = []
                r = row + 1
                while r <= 9:
                    next_cell = f"{col}{r}"
                    if isinstance(board.get(next_cell), CeldaNormal):
                        cells.append(next_cell)
                        r += 1
                    else:
                        break
                groups.append({"type": "vertical", "sum": celda.sum_vertical, "cells": cells})

    return groups

def map_celdas_to_grupos(groups):
    """
    Crea un mapeo inverso de celdas a los grupos a los que pertenecen.
    Esto permite encontrar rápidamente todas las restricciones que afectan a una celda dada.

    Args:
        groups (list): Una lista de diccionarios de grupos (como los devueltos por `detect_groups`).

    Returns:
        dict: Un diccionario donde las claves son los nombres de las celdas y los valores
              son listas de los diccionarios de grupos a los que pertenece cada celda.
    """
    mapping = {}
    for group in groups:
        for cell in group["cells"]:
            mapping.setdefault(cell, []).append(group)
    return mapping

def generate_combinations_for_sum(sum_value, count):
    """
    Genera todas las permutaciones únicas de números del 1 al 9 que suman un valor dado
    y tienen una longitud específica. Utiliza un caché para optimizar el rendimiento.

    Args:
        sum_value (int): La suma objetivo.
        count (int): El número de elementos en la combinación.

    Returns:
        list: Una lista de tuplas, donde cada tupla es una combinación válida.
    """
    key = (sum_value, count)
    if key not in comb_cache:
        # Genera permutaciones para asegurar dígitos únicos en la suma, como en Kakuro.
        comb_cache[key] = [comb for comb in itertools.permutations(range(1, 10), count) if sum(comb) == sum_value]
    return comb_cache[key]

def reduce_initial_domains(board, groups):
    """
    Reduce los dominios iniciales de las celdas blancas basándose en las combinaciones
    posibles para los grupos a los que pertenecen. Esto es una poda inicial del espacio de búsqueda.

    Args:
        board (dict): El diccionario del tablero.
        groups (list): Una lista de diccionarios de grupos.

    Returns:
        dict: Un diccionario donde las claves son los nombres de las celdas blancas y los valores
              son conjuntos de los números posibles para esa celda después de la poda inicial.
    """
    domains = {k: set(range(1, 10)) for k, v in board.items() if isinstance(v, CeldaNormal)}
    for group in groups:
        # Precalcula las combinaciones válidas para cada grupo
        group["combinations"] = generate_combinations_for_sum(group["sum"], len(group["cells"]))
        for i, cell in enumerate(group["cells"]):
            # Identifica los valores posibles para esta celda dentro de este grupo específico
            possible_values = set(comb[i] for comb in group["combinations"])
            # Intersecta el dominio actual de la celda con estos valores posibles
            domains[cell] &= possible_values
    return domains

def select_next_cell(assignment, domains):
    """
    Selecciona la próxima celda no asignada utilizando el heurístico de Mínimos Valores Restantes (MRV).
    Prioriza las celdas con el dominio más pequeño.

    Args:
        assignment (dict): Un diccionario de celdas ya asignadas (clave: valor).
        domains (dict): Un diccionario de los dominios actuales de todas las celdas.

    Returns:
        str: La clave de la celda seleccionada (ej. "A1"), o None si todas las celdas están asignadas.
    """
    unassigned = [v for v in domains if v not in assignment]
    if not unassigned:
        return None # Todas las celdas están asignadas o no hay celdas jugables
    # Retorna la celda con el dominio más pequeño
    return min(unassigned, key=lambda var: len(domains[var]))

def forward_check(cell, value, domains, groups_by_cell, assignment):
    """
    Realiza la verificación anticipada (Forward Checking) después de asignar un valor a una celda.
    Podra los dominios de las celdas no asignadas en los grupos relacionados.

    Args:
        cell (str): La clave de la celda a la que se le está asignando un valor.
        value (int): El valor que se le está asignando a la celda.
        domains (dict): Los dominios actuales de todas las celdas.
        groups_by_cell (dict): Mapeo de celdas a sus grupos asociados.
        assignment (dict): Las asignaciones actuales (debe incluir la asignación de 'cell').

    Returns:
        dict or None: Una copia de los dominios actualizados si la asignación es consistente,
                      o None si se detecta una inconsistencia (un dominio se vacía).
    """
    copy_domains = domains.copy()
    # Asignamos el valor temporalmente en la copia para las comprobaciones de consistencia
    # Nota: Se espera que 'assignment' sea una copia para que los cambios sean locales a la rama.
    assignment[cell] = value

    for group in groups_by_cell[cell]: # Para cada grupo al que pertenece la celda recién asignada
        for c in group["cells"]: # Itera sobre las celdas dentro de ese grupo
            if c in assignment:
                # Si la celda 'c' ya está asignada (incluyendo la 'cell' actual), saltar.
                # La consistencia con las celdas ya asignadas se verificará a través de las combinaciones.
                continue

            copy_domains[c] = domains[c].copy() # Copia el dominio de la celda vecina a verificar
            possible_values = set()
            for comb in group["combinations"]: # Para cada combinación válida del grupo
                # Verifica si la combinación es consistente con todas las celdas ya asignadas en este grupo,
                # y si la celda 'cell' tiene el 'value' que estamos probando.
                if all(
                    (assignment.get(group["cells"][i]) in [None, comb[i]]) # La celda en la combinación es None (no asignada) o coincide con su valor asignado
                    for i in range(len(group["cells"]))
                ) and comb[group["cells"].index(cell)] == value: # Y la celda actual (la que se está probando) coincide con su valor en la combinación
                    possible_values.add(comb[group["cells"].index(c)]) # Si es consistente, añade el valor posible para 'c'

            copy_domains[c] &= possible_values # Intersecta el dominio de 'c' con los valores posibles
            if not copy_domains[c]: # Si el dominio de 'c' se ha vaciado, es una inconsistencia
                return None # Retorna None para indicar fallo

    return copy_domains # Retorna los dominios podados si todo es consistente

def solver(normal_cells, groups_by_cell, domains):
    """
    Implementa el algoritmo de Backtracking con Forward Checking para resolver el Kakuro.

    Args:
        normal_cells (list): Una lista de las claves de todas las celdas normales (jugables).
        groups_by_cell (dict): Mapeo de celdas a los grupos a los que pertenecen.
        domains (dict): Los dominios iniciales (podados) de las celdas.

    Returns:
        dict or None: Un diccionario de asignaciones (clave: valor) si se encuentra una solución,
                      o None si no hay solución.
    """
    def backtrack(assignment, current_domains):
        """
        Función recursiva de backtracking.
        Args:
            assignment (dict): El diccionario de asignaciones actuales (celda: valor).
            current_domains (dict): Los dominios actuales de las celdas.
        Returns:
            dict or None: La solución parcial/completa, o None si esta rama no lleva a una solución.
        """
        # Caso base: Si todas las celdas normales han sido asignadas, se encontró una solución
        if len(assignment) == len(normal_cells):
            return assignment

        # Selecciona la próxima celda a asignar usando el heurístico MRV
        cell = select_next_cell(assignment, current_domains)
        if cell is None: # Si no hay más celdas para asignar (o todas tienen dominios vacíos)
            return None

        # Intenta cada valor en el dominio de la celda seleccionada
        for value in sorted(current_domains[cell]):
            new_assignment = assignment.copy() # Crea una copia de las asignaciones para la nueva rama
            # Realiza Forward Checking para probar la asignación y podar dominios
            new_domains = forward_check(cell, value, current_domains, groups_by_cell, new_assignment)

            if new_domains is not None: # Si la asignación es consistente
                # Llamada recursiva: Continúa el backtracking con la nueva asignación y dominios podados
                result = backtrack(new_assignment, new_domains)
                if result: # Si la llamada recursiva encontró una solución, la propaga hacia arriba
                    return result
        return None # Si ningún valor para esta celda lleva a una solución, retrocede

    # Inicia el proceso de backtracking con asignaciones vacías y los dominios iniciales
    return backtrack({}, domains)

def execute(file_path):
    """
    Función principal para ejecutar el solucionador de Kakuro.
    Carga el tablero, lo procesa, intenta resolverlo y muestra el resultado.

    Args:
        file_path (str): La ruta al archivo de texto del tablero de Kakuro.
    """
    keys = generate_keys()
    board = initialize_board(keys)
    load_board(file_path, board)

    print("\n📋 Tablero original:")
    print_board(board)

    groups = detect_groups(board)
    groups_by_cell = map_celdas_to_grupos(groups)
    playable_cells = [k for k, v in board.items() if isinstance(v, CeldaNormal)]

    domains = reduce_initial_domains(board, groups)

    start = time.time()
    solution = solver(playable_cells, groups_by_cell, domains)
    end = time.time()

    if solution:
        print("\n✅ Solución encontrada:")
        for cell, value in solution.items():
            board[cell].value = value
        print_board(board)
        print(f"\n🕒 Tiempo: {end - start:.2f} segundos")
    else:
        print("\n❌ No se encontró solución.")

if __name__ == "__main__":
    """
    Este es el punto de entrada principal del programa.
    Define una lista de rutas a archivos de tablero de Kakuro y ejecuta el solucionador para cada uno.
    El formato de los archivos de tablero es el siguiente:
      Cada línea en el archivo representa una celda en el tablero, leída de izquierda a derecha y de arriba a abajo.

      * Para una celda negra: se ingresa un "0".

      * Para una celda con restricciones de suma: se ingresa con el formato "suma_vertical|suma_horizontal".
          * Si una suma no tiene valor, se representa con un "0".
          * Ejemplos: "0|17" (solo suma horizontal), "43|0" (solo suma vertical).

      * Para una celda jugable (blanca): se ingresa un "#".

    Los tableros a resolver provienen del sitio web https://www.sudokumania.com.ar/kakuro/.

    """
    files_path = [ 'Boards\ProgIIIG1-Act08-KK5HVWCE-Board.txt', 'Boards\ProgIIIG1-Act08-KK5IXCOC-Board.txt','Boards\ProgIIIG1-Act08-KK5LMRDV-Board.txt' ]
    for i, path in enumerate(files_path):
        print(f"\n\n\n⚠️ Ejecutando Tablero {i+1}: {path}\n")
        execute(path)



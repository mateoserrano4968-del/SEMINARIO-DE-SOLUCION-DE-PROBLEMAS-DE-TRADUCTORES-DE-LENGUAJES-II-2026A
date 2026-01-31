"""
Ejercicio 1 - Mini Analizador Sintactico LR(1)
Gramatica: E → id + id
Analiza la cadena: a+b
"""

PESOS = 2
ID = 0
MAS = 1
E = 3

TABLA_LR = [
    [2,  0,  0,  1],
    [0,  0, -1,  0],
    [0,  3,  0,  0],
    [4,  0,  0,  0],
    [0,  0, -2,  0],
]
ID_REGLAS = [E]
LON_REGLAS = [3]


def analizar_lexico(cadena):
    """Convierte 'a+b' en tokens: [id, +, id, $]"""
    tokens = []
    i = 0
    while i < len(cadena):
        c = cadena[i]
        if c.isalpha() or c == '_':
            while i < len(cadena) and (cadena[i].isalnum() or cadena[i] == '_'):
                i += 1
            tokens.append(ID)
            continue
        elif c == '+':
            tokens.append(MAS)
        i += 1
    tokens.append(PESOS)
    return tokens


def analizar_sintactico(cadena):
    """Analiza la cadena usando el algoritmo LR(1) con pila de enteros."""
    tokens = analizar_lexico(cadena)
    pila = [PESOS, 0]
    pos = 0

    print("Ejercicio 1 - Gramatica: E -> id + id")
    print(f"Cadena a analizar: {cadena}")
    print("-" * 40)

    while True:
        estado = pila[-1]
        simbolo = tokens[pos] if pos < len(tokens) else PESOS
        columna = simbolo
        accion = TABLA_LR[estado][columna]

        print(f"Pila: {pila}  |  Entrada: {tokens[pos:]}  |  Accion: ", end="")

        if accion > 0:
            print(f"d{accion}")
            pila.append(simbolo)
            pila.append(accion)
            pos += 1

        elif accion < 0:
            if accion == -1:
                print("aceptacion")
                print("-" * 40)
                print("[OK] Cadena ACEPTADA")
                return True

            index_regla = -accion - 2
            lon = LON_REGLAS[index_regla]
            id_nt = ID_REGLAS[index_regla]

            print(f"r{index_regla + 1} (E->id+id)")

            for _ in range(lon * 2):
                pila.pop()

            estado_anterior = pila[-1]
            transicion = TABLA_LR[estado_anterior][id_nt]
            pila.append(id_nt)
            pila.append(transicion)

        else:
            print("ERROR")
            print("-" * 40)
            print("[ERROR] Cadena RECHAZADA")
            return False


if __name__ == "__main__":
    analizar_sintactico("a+b")


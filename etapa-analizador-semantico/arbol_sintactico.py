from typing import List, Optional

class NodoArbol:
    def __init__(self, tipo: str, valor: str = "", hijos: Optional[List['NodoArbol']] = None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos or []

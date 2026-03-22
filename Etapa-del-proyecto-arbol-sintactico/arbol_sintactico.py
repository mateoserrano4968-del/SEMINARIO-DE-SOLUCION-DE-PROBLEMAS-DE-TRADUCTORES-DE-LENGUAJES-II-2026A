"""
Construcción del árbol sintáctico (AST).
Nodos que representan la estructura del programa.
"""

from typing import List, Optional, Any

class NodoArbol:
    """Nodo base del árbol sintáctico."""
    def __init__(self, tipo: str, valor: str = "", hijos: Optional[List['NodoArbol']] = None):
        self.tipo = tipo
        self.valor = valor
        self.hijos = hijos or []

    def __str__(self) -> str:
        if self.valor:
            return f"{self.tipo}({self.valor})"
        return self.tipo

    def mostrar(self, nivel: int = 0) -> str:
        """Genera representación textual del árbol con sangría."""
        sangria = "  " * nivel
        if self.valor:
            linea = f"{sangria}<{self.tipo}> {self.valor}\n"
        else:
            linea = f"{sangria}<{self.tipo}>\n"
        for h in self.hijos:
            linea += h.mostrar(nivel + 1)
        return linea

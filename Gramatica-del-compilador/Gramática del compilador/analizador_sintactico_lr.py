"""Analizador sintáctico LR usando tablas del compilador."""

from typing import Any, Dict, List, Optional

from tokens import Token, TokenType
from cargador_gramatica import cargar_gramatica, Produccion

TOKEN_A_SIMBOLO = {
    TokenType.IDENTIFICADOR: "identificador", TokenType.ENTERO: "entero", TokenType.REAL: "real",
    TokenType.CADENA: "cadena", TokenType.TIPO: "tipo", TokenType.OP_SUMA: "opSuma", TokenType.OP_MUL: "opMul",
    TokenType.OP_RELAC: "opRelac", TokenType.OP_OR: "opOr", TokenType.OP_AND: "opAnd", TokenType.OP_NOT: "opNot",
    TokenType.OP_IGUALDAD: "opIgualdad", TokenType.PUNTO_COMA: ";", TokenType.COMA: ",",
    TokenType.PARENTESIS_ABRE: "(", TokenType.PARENTESIS_CIERRA: ")", TokenType.LLAVE_ABRE: "{",
    TokenType.LLAVE_CIERRA: "}", TokenType.ASIGNACION: "=", TokenType.IF: "if", TokenType.WHILE: "while",
    TokenType.RETURN: "return", TokenType.ELSE: "else", TokenType.EOF: "$",
}


class AnalizadorSintacticoLR:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicion = 0
        self.errores: List[str] = []
        self.tabla, self.producciones, self.simbolos = cargar_gramatica()

    def _simbolo(self) -> str:
        if self.posicion >= len(self.tokens):
            return "$"
        return TOKEN_A_SIMBOLO.get(self.tokens[self.posicion].tipo, "identificador")

    def _accion(self, estado: int, sim: str) -> Optional[str]:
        return self.tabla.get(str(estado), {}).get(sim)

    def analizar(self) -> bool:
        self.errores = []
        self.posicion = 0
        pila_estados = [0]
        pila_simbolos: List[Any] = []

        while True:
            estado = pila_estados[-1]
            sim = self._simbolo()
            token = self.tokens[self.posicion] if self.posicion < len(self.tokens) else None

            accion = self._accion(estado, sim)
            if accion is None or accion == "":
                self.errores.append(
                    f"Error sintáctico línea {token.linea}, col {token.columna}: "
                    f"no se esperaba '{token.valor}' (símbolo '{sim}')"
                )
                return False

            if accion in ("ACEPTAR", "r0"):
                return True

            if accion.startswith("d"):
                pila_estados.append(int(accion[1:]))
                pila_simbolos.append(token)
                self.posicion += 1
            elif accion.startswith("r"):
                num = int(accion[1:])
                idx = num - 1  # Tabla usa r1=R1, r2=R2... (1-based)
                if idx < 0 or idx >= len(self.producciones):
                    self.errores.append(f"Producción r{num} inválida")
                    return False
                prod = self.producciones[idx]
                for _ in range(prod.longitud):
                    pila_estados.pop()
                    pila_simbolos.pop()
                goto = self._accion(pila_estados[-1], prod.lhs)
                if goto is None or goto == "":
                    self.errores.append(f"Sin GOTO para {prod.lhs} en estado {pila_estados[-1]}")
                    return False
                pila_estados.append(int(goto))
                pila_simbolos.append(prod.lhs)
            else:
                self.errores.append(f"Acción desconocida '{accion}'")
                return False

"""
Analizador Sintáctico LR usando las tablas de la gramática del compilador (Modulo4).
"""

from typing import List, Optional, Dict, Any

from tokens import Token, TokenType
from .cargador_gramatica import cargar_gramatica, Produccion


TOKEN_A_SIMBOLO: Dict[TokenType, str] = {
    TokenType.IDENTIFICADOR: "identificador",
    TokenType.ENTERO: "entero",
    TokenType.REAL: "real",
    TokenType.CADENA: "cadena",
    TokenType.TIPO: "tipo",
    TokenType.OP_SUMA: "opSuma",
    TokenType.OP_MUL: "opMul",
    TokenType.OP_RELAC: "opRelac",
    TokenType.OP_OR: "opOr",
    TokenType.OP_AND: "opAnd",
    TokenType.OP_NOT: "opNot",
    TokenType.OP_IGUALDAD: "opIgualdad",
    TokenType.PUNTO_COMA: ";",
    TokenType.COMA: ",",
    TokenType.PARENTESIS_ABRE: "(",
    TokenType.PARENTESIS_CIERRA: ")",
    TokenType.LLAVE_ABRE: "{",
    TokenType.LLAVE_CIERRA: "}",
    TokenType.ASIGNACION: "=",
    TokenType.IF: "if",
    TokenType.WHILE: "while",
    TokenType.RETURN: "return",
    TokenType.ELSE: "else",
    TokenType.EOF: "$",
}


class ErrorSintactico(Exception):
    def __init__(self, mensaje: str, token: Optional[Token] = None):
        self.mensaje = mensaje
        self.token = token
        super().__init__(mensaje)


class AnalizadorSintacticoLR:
    """Analizador sintáctico LR(1) con tablas precalculadas."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicion = 0
        self.errores: List[str] = []
        self.tabla: Dict[str, Dict[str, str]] = {}
        self.producciones: List[Produccion] = []
        self.simbolos: List[str] = []
        self._cargar_tablas()

    def _cargar_tablas(self) -> None:
        self.tabla, self.producciones, self.simbolos = cargar_gramatica()

    def _simbolo_actual(self) -> str:
        if self.posicion >= len(self.tokens):
            return "$"
        token = self.tokens[self.posicion]
        return TOKEN_A_SIMBOLO.get(token.tipo, "identificador")

    def _token_actual(self) -> Optional[Token]:
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None

    def analizar(self) -> bool:
        self.errores = []
        self.posicion = 0
        pila_estados: List[int] = [0]
        pila_simbolos: List[Any] = []

        while True:
            estado_actual = pila_estados[-1]
            simbolo = self._simbolo_actual()
            token = self._token_actual()
            accion = self._obtener_accion(estado_actual, simbolo)

            if accion is None or accion == "":
                self._reportar_error(token, estado_actual, simbolo)
                return False

            if accion == "ACEPTAR" or accion == "r0":
                return True

            if accion.startswith("d"):
                nuevo_estado = int(accion[1:])
                pila_estados.append(nuevo_estado)
                pila_simbolos.append(token)
                self.posicion += 1

            elif accion.startswith("r"):
                num_prod = int(accion[1:])
                if num_prod >= len(self.producciones):
                    self.errores.append(f"Error: producción r{num_prod} inválida")
                    return False

                prod = self.producciones[num_prod]
                n = prod.longitud
                for _ in range(n):
                    pila_estados.pop()
                    pila_simbolos.pop()

                lhs = prod.lhs
                estado_antes = pila_estados[-1]
                goto = self._obtener_goto(estado_antes, lhs)
                if goto is None or goto == "":
                    self.errores.append(f"Error: sin GOTO para {lhs} en estado {estado_antes}")
                    return False

                nuevo_estado = int(goto)
                pila_estados.append(nuevo_estado)
                pila_simbolos.append(lhs)
            else:
                self.errores.append(f"Error: acción desconocida '{accion}'")
                return False

    def _obtener_accion(self, estado: int, simbolo: str) -> Optional[str]:
        estado_str = str(estado)
        if estado_str not in self.tabla:
            return None
        return self.tabla[estado_str].get(simbolo)

    def _obtener_goto(self, estado: int, simbolo: str) -> Optional[str]:
        return self._obtener_accion(estado, simbolo)

    def _reportar_error(self, token: Optional[Token], estado: int, simbolo: str) -> None:
        if token:
            self.errores.append(
                f"Error sintáctico en línea {token.linea}, columna {token.columna}: "
                f"no se esperaba '{token.valor}' (símbolo '{simbolo}'). Estado {estado}."
            )
        else:
            self.errores.append(f"Error sintáctico: entrada inesperada al final. Símbolo '{simbolo}'.")

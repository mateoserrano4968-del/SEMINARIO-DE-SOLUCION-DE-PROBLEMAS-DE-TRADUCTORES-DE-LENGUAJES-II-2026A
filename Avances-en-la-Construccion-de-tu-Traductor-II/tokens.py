
from enum import IntEnum


class TokenType(IntEnum):
    IDENTIFICADOR = 0
    ENTERO = 1
    REAL = 2
    CADENA = 3
    TIPO = 4
    OP_SUMA = 5
    OP_MUL = 6
    OP_RELAC = 7
    OP_OR = 8
    OP_AND = 9
    OP_NOT = 10
    OP_IGUALDAD = 11
    PUNTO_COMA = 12
    COMA = 13
    PARENTESIS_ABRE = 14
    PARENTESIS_CIERRA = 15
    LLAVE_ABRE = 16
    LLAVE_CIERRA = 17
    ASIGNACION = 18
    IF = 19
    WHILE = 20
    RETURN = 21
    ELSE = 22
    EOF = 23


class Token:

    def __init__(self, tipo: TokenType, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"Token({self.tipo.name}, '{self.valor}', línea {self.linea}, col {self.columna})"

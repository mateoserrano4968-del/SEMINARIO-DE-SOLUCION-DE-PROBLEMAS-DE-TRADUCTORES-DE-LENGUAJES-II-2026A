
from typing import List

from tokens import Token, TokenType


class ErrorSintactico(Exception):

    def __init__(self, mensaje: str, token: Token):
        self.mensaje = mensaje
        self.token = token
        super().__init__(mensaje)


class AnalizadorSintactico:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicion = 0
        self.errores: List[str] = []

    def _actual(self) -> Token:
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return self.tokens[-1] if self.tokens else Token(TokenType.EOF, '$', 0, 0)

    def _avanzar(self) -> Token:
        if self.posicion < len(self.tokens):
            tok = self.tokens[self.posicion]
            self.posicion += 1
            return tok
        return self._actual()

    def _coincide(self, *tipos: TokenType) -> bool:
        return self._actual().tipo in tipos

    def _consumir(self, tipo: TokenType, mensaje: str = "") -> Token:
        if self._coincide(tipo):
            return self._avanzar()
        t = self._actual()
        msg = mensaje or f"Se esperaba {tipo.name}, se encontró '{t.valor}'"
        self.errores.append(
            f"Error sintáctico en línea {t.linea}, columna {t.columna}: {msg}")
        raise ErrorSintactico(msg, t)

    def analizar(self) -> bool:
        self.errores = []
        self.posicion = 0
        try:
            self._programa()
            return len(self.errores) == 0
        except ErrorSintactico:
            return False

    def _programa(self) -> None:
        while not self._coincide(TokenType.EOF):
            self._declaracion()

    def _declaracion(self) -> None:
        self._tipo()
        self._consumir(TokenType.IDENTIFICADOR,
                       "Se esperaba identificador de función")
        self._consumir(TokenType.PARENTESIS_ABRE,
                       "Se esperaba '(' después del nombre de función")
        self._parametros()
        self._consumir(TokenType.PARENTESIS_CIERRA,
                       "Se esperaba ')' después de los parámetros")
        self._consumir(TokenType.LLAVE_ABRE,
                       "Se esperaba '{' para abrir el cuerpo de la función")
        self._lista_sentencias()
        self._consumir(TokenType.LLAVE_CIERRA,
                       "Se esperaba '}' para cerrar el cuerpo de la función")

    def _tipo(self) -> None:
        if not self._coincide(TokenType.TIPO):
            t = self._actual()
            self.errores.append(
                f"Error sintáctico en línea {t.linea}, columna {t.columna}: "
                f"Se esperaba tipo (int, float, void), se encontró '{t.valor}'")
            raise ErrorSintactico("Se esperaba tipo", t)
        self._avanzar()

    def _parametros(self) -> None:
        if self._coincide(TokenType.TIPO):
            self._tipo()
            self._consumir(TokenType.IDENTIFICADOR,
                           "Se esperaba identificador de parámetro")
            while self._coincide(TokenType.COMA):
                self._avanzar()
                self._tipo()
                self._consumir(TokenType.IDENTIFICADOR,
                               "Se esperaba identificador de parámetro")

    def _lista_sentencias(self) -> None:
        while not self._coincide(TokenType.LLAVE_CIERRA, TokenType.EOF):
            self._sentencia()

    def _sentencia(self) -> None:
        if self._coincide(TokenType.IF):
            self._sentencia_if()
        elif self._coincide(TokenType.WHILE):
            self._sentencia_while()
        elif self._coincide(TokenType.RETURN):
            self._sentencia_return()
        elif self._coincide(TokenType.TIPO):
            self._sentencia_declaracion()
        elif self._coincide(TokenType.LLAVE_ABRE):
            self._bloque()
        else:
            self._sentencia_expr()

    def _sentencia_declaracion(self) -> None:
        self._tipo()
        self._consumir(TokenType.IDENTIFICADOR,
                       "Se esperaba identificador de variable")
        if self._coincide(TokenType.ASIGNACION):
            self._avanzar()
            self._expresion()
        self._consumir(TokenType.PUNTO_COMA,
                       "Se esperaba ';' después de la declaración")

    def _sentencia_if(self) -> None:
        self._avanzar()
        self._consumir(TokenType.PARENTESIS_ABRE,
                       "Se esperaba '(' después de if")
        self._expresion()
        self._consumir(TokenType.PARENTESIS_CIERRA,
                       "Se esperaba ')' después de la condición")
        self._sentencia()
        if self._coincide(TokenType.ELSE):
            self._avanzar()
            self._sentencia()

    def _sentencia_while(self) -> None:
        self._avanzar()
        self._consumir(TokenType.PARENTESIS_ABRE,
                       "Se esperaba '(' después de while")
        self._expresion()
        self._consumir(TokenType.PARENTESIS_CIERRA,
                       "Se esperaba ')' después de la condición")
        self._sentencia()

    def _sentencia_return(self) -> None:
        self._avanzar()
        if not self._coincide(TokenType.PUNTO_COMA):
            self._expresion()
        self._consumir(TokenType.PUNTO_COMA,
                       "Se esperaba ';' después de return")

    def _bloque(self) -> None:
        self._consumir(TokenType.LLAVE_ABRE,
                       "Se esperaba '{'")
        self._lista_sentencias()
        self._consumir(TokenType.LLAVE_CIERRA,
                       "Se esperaba '}'")

    def _sentencia_expr(self) -> None:
        self._expresion()
        self._consumir(TokenType.PUNTO_COMA,
                       "Se esperaba ';' al final de la sentencia")

    def _expresion(self) -> None:
        self._expresion_asignacion()

    def _expresion_asignacion(self) -> None:
        if (self._coincide(TokenType.IDENTIFICADOR) and
                self.posicion + 1 < len(self.tokens) and
                self.tokens[self.posicion + 1].tipo == TokenType.ASIGNACION):
            self._avanzar()
            self._avanzar()
            self._expresion_asignacion()
        else:
            self._expresion_or()

    def _expresion_or(self) -> None:
        self._expresion_and()
        while self._coincide(TokenType.OP_OR):
            self._avanzar()
            self._expresion_and()

    def _expresion_and(self) -> None:
        self._expresion_igualdad()
        while self._coincide(TokenType.OP_AND):
            self._avanzar()
            self._expresion_igualdad()

    def _expresion_igualdad(self) -> None:
        self._expresion_relacion()
        while self._coincide(TokenType.OP_IGUALDAD):
            self._avanzar()
            self._expresion_relacion()

    def _expresion_relacion(self) -> None:
        self._expresion_aditiva()
        while self._coincide(TokenType.OP_RELAC):
            self._avanzar()
            self._expresion_aditiva()

    def _expresion_aditiva(self) -> None:
        self._expresion_multiplicativa()
        while self._coincide(TokenType.OP_SUMA):
            self._avanzar()
            self._expresion_multiplicativa()

    def _expresion_multiplicativa(self) -> None:
        self._expresion_unaria()
        while self._coincide(TokenType.OP_MUL):
            self._avanzar()
            self._expresion_unaria()

    def _expresion_unaria(self) -> None:
        if self._coincide(TokenType.OP_NOT):
            self._avanzar()
            self._expresion_unaria()
        elif self._coincide(TokenType.OP_SUMA) and self._actual().valor == '-':
            self._avanzar()
            self._expresion_unaria()
        else:
            self._expresion_primaria()

    def _expresion_primaria(self) -> None:
        if self._coincide(TokenType.IDENTIFICADOR, TokenType.ENTERO,
                          TokenType.REAL, TokenType.CADENA):
            self._avanzar()
        elif self._coincide(TokenType.PARENTESIS_ABRE):
            self._avanzar()
            self._expresion()
            self._consumir(TokenType.PARENTESIS_CIERRA,
                           "Se esperaba ')' para cerrar expresión")
        else:
            t = self._actual()
            self.errores.append(
                f"Error sintáctico en línea {t.linea}, columna {t.columna}: "
                f"Se esperaba expresión (identificador, número, cadena o '('), "
                f"se encontró '{t.valor}'")
            raise ErrorSintactico("Se esperaba expresión", t)

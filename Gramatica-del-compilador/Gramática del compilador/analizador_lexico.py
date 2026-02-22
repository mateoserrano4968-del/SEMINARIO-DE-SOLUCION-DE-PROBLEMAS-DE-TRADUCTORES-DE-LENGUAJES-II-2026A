"""Analizador léxico del compilador."""

from typing import List, Optional

from tokens import Token, TokenType


class AnalizadorLexico:
    PALABRAS_RESERVADAS = {
        'if': TokenType.IF, 'while': TokenType.WHILE, 'return': TokenType.RETURN,
        'else': TokenType.ELSE, 'int': TokenType.TIPO, 'float': TokenType.TIPO, 'void': TokenType.TIPO
    }

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens: List[Token] = []
        self.errores: List[str] = []

    def _sig(self) -> Optional[str]:
        return self.codigo[self.posicion] if self.posicion < len(self.codigo) else None

    def _avanzar(self, n: int = 1):
        for _ in range(n):
            if self.posicion < len(self.codigo):
                if self.codigo[self.posicion] == '\n':
                    self.linea += 1
                    self.columna = 1
                else:
                    self.columna += 1
                self.posicion += 1

    def _id(self) -> Optional[Token]:
        if not self._sig() or not self._sig().isalpha():
            return None
        inicio, col = self.posicion, self.columna
        self._avanzar()
        while self._sig() and self._sig().isalnum():
            self._avanzar()
        v = self.codigo[inicio:self.posicion]
        return Token(self.PALABRAS_RESERVADAS.get(v, TokenType.IDENTIFICADOR), v, self.linea, col)

    def _num(self) -> Optional[Token]:
        if not self._sig() or not self._sig().isdigit():
            return None
        inicio, col = self.posicion, self.columna
        while self._sig() and self._sig().isdigit():
            self._avanzar()
        if self._sig() == '.' and self.posicion + 1 < len(self.codigo) and self.codigo[self.posicion + 1].isdigit():
            self._avanzar()
            while self._sig() and self._sig().isdigit():
                self._avanzar()
            return Token(TokenType.REAL, self.codigo[inicio:self.posicion], self.linea, col)
        return Token(TokenType.ENTERO, self.codigo[inicio:self.posicion], self.linea, col)

    def _cadena(self) -> Optional[Token]:
        if self._sig() != '"':
            return None
        col = self.columna
        self._avanzar()
        inicio = self.posicion
        while self._sig() and self._sig() != '"':
            if self._sig() == '\n':
                self.errores.append(f"Error léxico: Cadena sin cerrar línea {self.linea}, col {col}")
                return None
            self._avanzar()
        if not self._sig():
            self.errores.append(f"Error léxico: Cadena sin cerrar línea {self.linea}, col {col}")
            return None
        v = self.codigo[inicio:self.posicion]
        self._avanzar()
        return Token(TokenType.CADENA, v, self.linea, col)

    def analizar(self) -> List[Token]:
        self.tokens, self.errores = [], []
        self.posicion, self.linea, self.columna = 0, 1, 1

        while True:
            while self._sig() and self._sig() in ' \t\n\r':
                self._avanzar()
            if self.posicion >= len(self.codigo):
                break
            c = self._sig()
            if c.isalpha():
                t = self._id()
                if t:
                    self.tokens.append(t)
            elif c.isdigit():
                t = self._num()
                if t:
                    self.tokens.append(t)
            elif c == '"':
                t = self._cadena()
                if t:
                    self.tokens.append(t)
            elif c in '+-':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.OP_SUMA, c, self.linea, col))
            elif c in '*/':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.OP_MUL, c, self.linea, col))
            elif c in '<>':
                col = self.columna
                self._avanzar()
                if self._sig() == '=':
                    self._avanzar()
                    self.tokens.append(Token(TokenType.OP_RELAC, c + '=', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.OP_RELAC, c, self.linea, col))
            elif c == '=':
                col = self.columna
                self._avanzar()
                if self._sig() == '=':
                    self._avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '==', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.ASIGNACION, '=', self.linea, col))
            elif c == '!':
                col = self.columna
                self._avanzar()
                if self._sig() == '=':
                    self._avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '!=', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.OP_NOT, '!', self.linea, col))
            elif c == '&':
                col = self.columna
                self._avanzar()
                if self._sig() == '&':
                    self._avanzar()
                    self.tokens.append(Token(TokenType.OP_AND, '&&', self.linea, col))
                else:
                    self.errores.append(f"Error léxico: '&' incompleto línea {self.linea}, col {col}")
            elif c == '|':
                col = self.columna
                self._avanzar()
                if self._sig() == '|':
                    self._avanzar()
                    self.tokens.append(Token(TokenType.OP_OR, '||', self.linea, col))
                else:
                    self.errores.append(f"Error léxico: '|' incompleto línea {self.linea}, col {col}")
            elif c == ';':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.PUNTO_COMA, ';', self.linea, col))
            elif c == ',':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.COMA, ',', self.linea, col))
            elif c == '(':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_ABRE, '(', self.linea, col))
            elif c == ')':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_CIERRA, ')', self.linea, col))
            elif c == '{':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.LLAVE_ABRE, '{', self.linea, col))
            elif c == '}':
                col = self.columna
                self._avanzar()
                self.tokens.append(Token(TokenType.LLAVE_CIERRA, '}', self.linea, col))
            else:
                self.errores.append(f"Error léxico: '{c}' no reconocido línea {self.linea}, col {self.columna}")
                self._avanzar()

        self.tokens.append(Token(TokenType.EOF, '$', self.linea, self.columna))
        return self.tokens

    def tiene_errores(self) -> bool:
        return len(self.errores) > 0

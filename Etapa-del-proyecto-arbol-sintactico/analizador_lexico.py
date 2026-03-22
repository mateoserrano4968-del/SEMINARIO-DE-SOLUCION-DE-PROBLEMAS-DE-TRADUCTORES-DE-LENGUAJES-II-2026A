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

    def siguiente_caracter(self) -> Optional[str]:
        if self.posicion >= len(self.codigo):
            return None
        return self.codigo[self.posicion]

    def avanzar(self, n: int = 1) -> None:
        for _ in range(n):
            if self.posicion < len(self.codigo):
                if self.codigo[self.posicion] == '\n':
                    self.linea += 1
                    self.columna = 1
                else:
                    self.columna += 1
                self.posicion += 1

    def _reconocer_identificador(self) -> Optional[Token]:
        inicio = self.posicion
        inicio_col = self.columna
        if not self.siguiente_caracter() or not self.siguiente_caracter().isalpha():
            return None
        self.avanzar()
        while self.siguiente_caracter() and (self.siguiente_caracter().isalnum() or self.siguiente_caracter() == '_'):
            self.avanzar()
        valor = self.codigo[inicio:self.posicion]
        tipo = self.PALABRAS_RESERVADAS.get(valor, TokenType.IDENTIFICADOR)
        return Token(tipo, valor, self.linea, inicio_col)

    def _reconocer_numero(self) -> Optional[Token]:
        inicio = self.posicion
        inicio_col = self.columna
        if not self.siguiente_caracter() or not self.siguiente_caracter().isdigit():
            return None
        while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
            self.avanzar()
        if self.siguiente_caracter() == '.' and self.posicion + 1 < len(self.codigo) and self.codigo[self.posicion + 1].isdigit():
            self.avanzar()
            while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
                self.avanzar()
            return Token(TokenType.REAL, self.codigo[inicio:self.posicion], self.linea, inicio_col)
        return Token(TokenType.ENTERO, self.codigo[inicio:self.posicion], self.linea, inicio_col)

    def analizar(self) -> List[Token]:
        self.tokens = []
        self.errores = []
        self.posicion = 0
        self.linea = 1
        self.columna = 1

        while self.posicion < len(self.codigo):
            while self.siguiente_caracter() and self.siguiente_caracter() in ' \t\n\r':
                self.avanzar()
            if self.posicion >= len(self.codigo):
                break
            char = self.siguiente_caracter()
            if char.isalpha():
                t = self._reconocer_identificador()
                if t:
                    self.tokens.append(t)
            elif char.isdigit():
                t = self._reconocer_numero()
                if t:
                    self.tokens.append(t)
            elif char in '+-':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.OP_SUMA, char, self.linea, c))
            elif char in '*/':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.OP_MUL, char, self.linea, c))
            elif char in '<>':
                c = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_RELAC, char + '=', self.linea, c))
                else:
                    self.tokens.append(Token(TokenType.OP_RELAC, char, self.linea, c))
            elif char == '=':
                c = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '==', self.linea, c))
                else:
                    self.tokens.append(Token(TokenType.ASIGNACION, '=', self.linea, c))
            elif char == '!':
                c = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '!=', self.linea, c))
                else:
                    self.tokens.append(Token(TokenType.OP_NOT, '!', self.linea, c))
            elif char == '&':
                c = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '&':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_AND, '&&', self.linea, c))
                else:
                    self.errores.append(f"Error: '&' incompleto línea {self.linea}")
                    self.avanzar()
            elif char == '|':
                c = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '|':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_OR, '||', self.linea, c))
                else:
                    self.errores.append(f"Error: '|' incompleto línea {self.linea}")
                    self.avanzar()
            elif char == ';':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PUNTO_COMA, ';', self.linea, c))
            elif char == ',':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.COMA, ',', self.linea, c))
            elif char == '(':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_ABRE, '(', self.linea, c))
            elif char == ')':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_CIERRA, ')', self.linea, c))
            elif char == '{':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.LLAVE_ABRE, '{', self.linea, c))
            elif char == '}':
                c = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.LLAVE_CIERRA, '}', self.linea, c))
            else:
                self.errores.append(f"Carácter no reconocido '{char}' línea {self.linea}")
                self.avanzar()

        self.tokens.append(Token(TokenType.EOF, '$', self.linea, self.columna))
        return self.tokens

    def tiene_errores(self) -> bool:
        return len(self.errores) > 0

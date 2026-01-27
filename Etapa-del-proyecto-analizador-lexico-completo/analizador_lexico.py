"""
Analizador Léxico - Proyecto Taller Compiladores
Reconoce todos los símbolos léxicos especificados en simbolos_lexicos.pdf
"""

import re
import sys
from enum import IntEnum
from typing import List, Tuple, Optional


class TokenType(IntEnum):
    """Tipos de tokens según la especificación"""
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
    PUNTO_COMA = 12  # ;
    COMA = 13  # ,
    PARENTESIS_ABRE = 14  # (
    PARENTESIS_CIERRA = 15  # )
    LLAVE_ABRE = 16  # {
    LLAVE_CIERRA = 17  # }
    ASIGNACION = 18  # =
    IF = 19
    WHILE = 20
    RETURN = 21
    ELSE = 22
    EOF = 23  # $


class Token:
    """Representa un token reconocido"""
    def __init__(self, tipo: TokenType, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
    
    def __repr__(self):
        return f"Token({self.tipo.name}, '{self.valor}', línea {self.linea}, col {self.columna})"


class AnalizadorLexico:
    """Analizador léxico que reconoce todos los símbolos especificados"""
    
    # Palabras reservadas
    PALABRAS_RESERVADAS = {
        'if': TokenType.IF,
        'while': TokenType.WHILE,
        'return': TokenType.RETURN,
        'else': TokenType.ELSE,
        'int': TokenType.TIPO,
        'float': TokenType.TIPO,
        'void': TokenType.TIPO
    }
    
    # Operadores de dos caracteres (deben verificarse primero)
    OPERADORES_DOBLES = {
        '<=': TokenType.OP_RELAC,
        '>=': TokenType.OP_RELAC,
        '==': TokenType.OP_IGUALDAD,
        '!=': TokenType.OP_IGUALDAD,
        '&&': TokenType.OP_AND,
        '||': TokenType.OP_OR
    }
    
    # Operadores de un carácter
    OPERADORES_SIMPLES = {
        '+': TokenType.OP_SUMA,
        '-': TokenType.OP_SUMA,
        '*': TokenType.OP_MUL,
        '/': TokenType.OP_MUL,
        '<': TokenType.OP_RELAC,
        '>': TokenType.OP_RELAC,
        '!': TokenType.OP_NOT,
        ';': TokenType.PUNTO_COMA,
        ',': TokenType.COMA,
        '(': TokenType.PARENTESIS_ABRE,
        ')': TokenType.PARENTESIS_CIERRA,
        '{': TokenType.LLAVE_ABRE,
        '}': TokenType.LLAVE_CIERRA
    }
    
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self.errores = []
    
    def siguiente_caracter(self) -> Optional[str]:
        """Obtiene el siguiente carácter sin avanzar"""
        if self.posicion >= len(self.codigo):
            return None
        return self.codigo[self.posicion]
    
    def avanzar(self, n: int = 1):
        """Avanza la posición n caracteres"""
        for _ in range(n):
            if self.posicion < len(self.codigo):
                if self.codigo[self.posicion] == '\n':
                    self.linea += 1
                    self.columna = 1
                else:
                    self.columna += 1
                self.posicion += 1
    
    def ignorar_espacios(self):
        """Ignora espacios en blanco y saltos de línea"""
        while self.posicion < len(self.codigo):
            char = self.codigo[self.posicion]
            if char in ' \t\n\r':
                self.avanzar()
            else:
                break
    
    def reconocer_identificador(self) -> Optional[Token]:
        """Reconoce identificadores: letra (letra|digito)*"""
        inicio = self.posicion
        inicio_col = self.columna
        if not self.siguiente_caracter() or not self.siguiente_caracter().isalpha():
            return None
        
        self.avanzar()
        while self.siguiente_caracter() and self.siguiente_caracter().isalnum():
            self.avanzar()
        
        valor = self.codigo[inicio:self.posicion]
        tipo = self.PALABRAS_RESERVADAS.get(valor, TokenType.IDENTIFICADOR)
        return Token(tipo, valor, self.linea, inicio_col)
    
    def reconocer_numero(self) -> Optional[Token]:
        """Reconoce enteros y reales"""
        inicio = self.posicion
        inicio_col = self.columna
        if not self.siguiente_caracter() or not self.siguiente_caracter().isdigit():
            return None
        
        while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
            self.avanzar()
        
        # Verificar si es real
        if self.siguiente_caracter() == '.' and self.posicion + 1 < len(self.codigo) and self.codigo[self.posicion + 1].isdigit():
            self.avanzar()  # punto
            while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
                self.avanzar()
            return Token(TokenType.REAL, self.codigo[inicio:self.posicion], self.linea, inicio_col)
        else:
            return Token(TokenType.ENTERO, self.codigo[inicio:self.posicion], self.linea, inicio_col)
    
    def reconocer_cadena(self) -> Optional[Token]:
        """Reconoce cadenas entre comillas"""
        inicio_col = self.columna
        if self.siguiente_caracter() != '"':
            return None
        
        self.avanzar()  # comilla inicial
        inicio = self.posicion
        
        while self.siguiente_caracter() and self.siguiente_caracter() != '"':
            if self.siguiente_caracter() == '\n':
                self.errores.append(f"Error: Cadena sin cerrar en línea {self.linea}, columna {inicio_col}")
                return None
            self.avanzar()
        
        if not self.siguiente_caracter():
            self.errores.append(f"Error: Cadena sin cerrar en línea {self.linea}, columna {inicio_col}")
            return None
        
        valor = self.codigo[inicio:self.posicion]
        self.avanzar()  # comilla final
        return Token(TokenType.CADENA, valor, self.linea, inicio_col)
    
    
    def analizar(self) -> List[Token]:
        """Analiza el código fuente usando bucle infinito y switch"""
        self.tokens = []
        self.errores = []
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        
        # Bucle infinito
        while True:
            # Ignorar espacios
            while self.siguiente_caracter() and self.siguiente_caracter() in ' \t\n\r':
                self.avanzar()
            
            if self.posicion >= len(self.codigo):
                break
            
            char = self.siguiente_caracter()
            if not char:
                break
            
            # Switch para procesar cada carácter
            if char.isalpha():
                token = self.reconocer_identificador()
                if token:
                    self.tokens.append(token)
            elif char.isdigit():
                token = self.reconocer_numero()
                if token:
                    self.tokens.append(token)
            elif char == '"':
                token = self.reconocer_cadena()
                if token:
                    self.tokens.append(token)
            elif char == '+' or char == '-':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.OP_SUMA, char, self.linea, col))
            elif char == '*' or char == '/':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.OP_MUL, char, self.linea, col))
            elif char == '<' or char == '>':
                col = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_RELAC, char + '=', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.OP_RELAC, char, self.linea, col))
            elif char == '=':
                col = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '==', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.ASIGNACION, '=', self.linea, col))
            elif char == '!':
                col = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '=':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_IGUALDAD, '!=', self.linea, col))
                else:
                    self.tokens.append(Token(TokenType.OP_NOT, '!', self.linea, col))
            elif char == '&':
                col = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '&':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_AND, '&&', self.linea, col))
                else:
                    self.errores.append(f"Error: '&' incompleto en línea {self.linea}, columna {col}")
            elif char == '|':
                col = self.columna
                self.avanzar()
                if self.siguiente_caracter() == '|':
                    self.avanzar()
                    self.tokens.append(Token(TokenType.OP_OR, '||', self.linea, col))
                else:
                    self.errores.append(f"Error: '|' incompleto en línea {self.linea}, columna {col}")
            elif char == ';':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PUNTO_COMA, ';', self.linea, col))
            elif char == ',':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.COMA, ',', self.linea, col))
            elif char == '(':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_ABRE, '(', self.linea, col))
            elif char == ')':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.PARENTESIS_CIERRA, ')', self.linea, col))
            elif char == '{':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.LLAVE_ABRE, '{', self.linea, col))
            elif char == '}':
                col = self.columna
                self.avanzar()
                self.tokens.append(Token(TokenType.LLAVE_CIERRA, '}', self.linea, col))
            else:
                self.errores.append(f"Error: Carácter no reconocido '{char}' en línea {self.linea}, columna {self.columna}")
                self.avanzar()
        
        self.tokens.append(Token(TokenType.EOF, '$', self.linea, self.columna))
        return self.tokens
    
    def imprimir_tokens(self):
        """Imprime todos los tokens reconocidos"""
        print("=" * 60)
        print("TOKENS RECONOCIDOS:")
        print("=" * 60)
        print(f"{'Tipo':<20} {'Valor':<20} {'Línea':<10} {'Columna':<10}")
        print("-" * 60)
        
        for token in self.tokens:
            print(f"{token.tipo.name:<20} {token.valor:<20} {token.linea:<10} {token.columna:<10}")
        
        print("=" * 60)
        print(f"Total de tokens: {len(self.tokens)}")
        
        if self.errores:
            print("\n" + "=" * 60)
            print("ERRORES ENCONTRADOS:")
            print("=" * 60)
            for error in self.errores:
                print(error)


def main():
    """Función principal para probar el analizador léxico"""
    print("Analizador Léxico - Proyecto Taller Compiladores")
    print("=" * 60)
    
    # Obtener el nombre del archivo desde los argumentos de línea de comandos
    if len(sys.argv) > 1:
        nombre_archivo = sys.argv[1]
    else:
        nombre_archivo = input("\nIngresa el nombre del archivo a analizar: ").strip()
    
    if not nombre_archivo:
        print("\nError: No se especificó un archivo para analizar.")
        return
    
    try:
        # Leer el archivo
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            codigo = archivo.read()
        
        if not codigo.strip():
            print("\nError: El archivo está vacío.")
            return
        
        print("\n" + "=" * 60)
        print(f"Archivo: {nombre_archivo}")
        print("Código a analizar:")
        print("=" * 60)
        print(codigo)
        print("\n")
        
        analizador = AnalizadorLexico(codigo)
        tokens = analizador.analizar()
        analizador.imprimir_tokens()
        
    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo '{nombre_archivo}'.")
    except PermissionError:
        print(f"\nError: No tienes permisos para leer el archivo '{nombre_archivo}'.")
    except Exception as e:
        print(f"\nError: {e}")
    
    # Pausa para que no se cierre la ventana (solo si hay entrada disponible)
    try:
        input("\nPresiona Enter para salir...")
    except EOFError:
        pass  # Si no hay entrada disponible, continuar


if __name__ == "__main__":
    main()

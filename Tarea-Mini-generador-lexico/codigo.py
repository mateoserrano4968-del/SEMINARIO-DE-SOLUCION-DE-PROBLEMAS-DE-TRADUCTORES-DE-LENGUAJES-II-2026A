"""
Analizador Léxico Simple
Reconoce solo identificadores y números reales

Identificadores: letra(letra|digito)*
Números reales: entero.entero+
"""

from enum import IntEnum
from typing import List, Optional
import sys
import os


class TokenType(IntEnum):
    """Tipos de tokens"""
    IDENTIFICADOR = 0
    REAL = 1
    EOF = 2  # Fin de archivo


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
    """Analizador léxico simple que reconoce identificadores y números reales"""
    
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
    
    def reconocer_identificador(self) -> Optional[Token]:
        """Reconoce identificadores: letra(letra|digito)*"""
        inicio = self.posicion
        inicio_col = self.columna
        
        if not self.siguiente_caracter() or not self.siguiente_caracter().isalpha():
            return None
        
        self.avanzar()
        while self.siguiente_caracter() and (self.siguiente_caracter().isalnum()):
            self.avanzar()
        
        valor = self.codigo[inicio:self.posicion]
        return Token(TokenType.IDENTIFICADOR, valor, self.linea, inicio_col)
    
    def reconocer_real(self) -> Optional[Token]:
        """Reconoce números reales: entero.entero+"""
        inicio = self.posicion
        inicio_col = self.columna
        
        if not self.siguiente_caracter() or not self.siguiente_caracter().isdigit():
            return None
        
        # Leer parte entera
        while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
            self.avanzar()
        
        # Debe tener un punto
        if self.siguiente_caracter() != '.':
            return None
        
        self.avanzar()  # avanzar el punto
        
        # Debe tener al menos un dígito después del punto (entero+)
        if not self.siguiente_caracter() or not self.siguiente_caracter().isdigit():
            return None
        
        # Leer parte decimal (uno o más dígitos)
        while self.siguiente_caracter() and self.siguiente_caracter().isdigit():
            self.avanzar()
        
        valor = self.codigo[inicio:self.posicion]
        return Token(TokenType.REAL, valor, self.linea, inicio_col)
    
    def analizar(self) -> List[Token]:
        """Analiza el código fuente usando bucle infinito y switch"""
        self.tokens = []
        self.errores = []
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        
        # Bucle infinito
        while True:
            # Ignorar espacios en blanco
            while self.siguiente_caracter() and self.siguiente_caracter() in ' \t\n\r':
                self.avanzar()
            
            if self.posicion >= len(self.codigo):
                break
            
            char = self.siguiente_caracter()
            if not char:
                break
            
            # Switch para procesar cada carácter
            if char.isalpha():
                # Es una letra: puede ser identificador
                token = self.reconocer_identificador()
                if token:
                    self.tokens.append(token)
                else:
                    self.errores.append(f"Error: No se pudo reconocer identificador en línea {self.linea}, columna {self.columna}")
                    self.avanzar()
            elif char.isdigit():
                # Es un dígito: puede ser número real
                token = self.reconocer_real()
                if token:
                    self.tokens.append(token)
                else:
                    # Si no es real válido, es un error (solo aceptamos reales, no enteros)
                    self.errores.append(f"Error: Número no válido en línea {self.linea}, columna {self.columna}")
                    # Avanzar para no quedarse atascado
                    while self.siguiente_caracter() and (self.siguiente_caracter().isdigit() or self.siguiente_caracter() == '.'):
                        self.avanzar()
            else:
                # Carácter no reconocido
                self.errores.append(f"Error: Carácter no reconocido '{char}' en línea {self.linea}, columna {self.columna}")
                self.avanzar()
        
        # Agregar token EOF
        self.tokens.append(Token(TokenType.EOF, '$', self.linea, self.columna))
        return self.tokens
    
    def imprimir_tokens(self):
        """Imprime todos los tokens reconocidos"""
        print("=" * 60)
        print("ANALIZADOR LÉXICO SIMPLE")
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


def leer_archivo(nombre_archivo: str) -> str:
    """Lee el contenido de un archivo"""
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return archivo.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{nombre_archivo}'")
        return None
    except Exception as e:
        print(f"Error al leer el archivo '{nombre_archivo}': {e}")
        return None


def main():
    """Función principal para probar el analizador léxico"""
    print("Analizador Léxico Simple")
    print("Reconoce: Identificadores y Números Reales")
    print("=" * 60)
    
    codigo = None
    
    # Si se proporciona un archivo como argumento
    if len(sys.argv) > 1:
        nombre_archivo = sys.argv[1]
        print(f"\nLeyendo archivo: {nombre_archivo}")
        print("=" * 60)
        codigo = leer_archivo(nombre_archivo)
        
        if codigo is None:
            return
        
        print("\nContenido del archivo:")
        print("-" * 60)
        print(codigo)
        print("-" * 60)
    else:
        # Siempre preguntar al usuario
        print("\nOpciones:")
        print("1. Ingresar nombre de archivo")
        print("2. Ingresar código manualmente")
        
        try:
            opcion = input("\nSelecciona una opción (1 o 2): ").strip()
            
            if opcion == "1":
                nombre_archivo = input("Ingresa el nombre del archivo: ").strip()
                codigo = leer_archivo(nombre_archivo)
                if codigo:
                    print("\nContenido del archivo:")
                    print("-" * 60)
                    print(codigo)
                    print("-" * 60)
            elif opcion == "2":
                print("\nIngresa tu código (presiona Ctrl+Z y Enter para terminar):")
                print("=" * 60)
                lineas = []
                while True:
                    try:
                        linea = input()
                        lineas.append(linea)
                    except EOFError:
                        break
                codigo = "\n".join(lineas)
            else:
                print("Opción no válida.")
                return
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario.")
            return
    
    # Analizar el código si se obtuvo
    if codigo and codigo.strip():
        print("\n" + "=" * 60)
        print("ANALIZANDO CÓDIGO...")
        print("=" * 60)
        
        analizador = AnalizadorLexico(codigo)
        tokens = analizador.analizar()
        analizador.imprimir_tokens()
    else:
        print("\nNo hay código para analizar.")
    
    # Pausa para que no se cierre la ventana
    try:
        input("\nPresiona Enter para salir...")
    except EOFError:
        pass


if __name__ == "__main__":
    main()

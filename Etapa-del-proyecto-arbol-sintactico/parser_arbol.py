"""
Parser que construye el árbol sintáctico.
Soporta: DefVar (int a;), DefFunc con parámetros, return, asignaciones, llamadas a función.
"""

from typing import List, Optional
from tokens import Token, TokenType
from arbol_sintactico import NodoArbol


class ParserArbol:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errores: List[str] = []

    def _actual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1] if self.tokens else Token(TokenType.EOF, '$', 0, 0)

    def _avanzar(self) -> Token:
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return self._actual()

    def _coincide(self, *tipos: TokenType) -> bool:
        return self._actual().tipo in tipos

    def _consumir(self, tipo: TokenType, msg: str = "") -> Token:
        if self._coincide(tipo):
            return self._avanzar()
        t = self._actual()
        self.errores.append(f"Error línea {t.linea}: se esperaba {tipo.name}, se encontró '{t.valor}'")
        raise ValueError(msg or f"Esperaba {tipo.name}")

    def parsear(self) -> Optional[NodoArbol]:
        """Parsea el programa y retorna el nodo raíz del árbol."""
        self.errores = []
        self.pos = 0
        try:
            return self._programa()
        except (ValueError, IndexError):
            return None

    def _programa(self) -> NodoArbol:
        hijos: List[NodoArbol] = []
        while not self._coincide(TokenType.EOF):
            nodo = self._definicion()
            if nodo:
                hijos.append(nodo)
        return NodoArbol("Programa", "", hijos)

    def _definicion(self) -> Optional[NodoArbol]:
        if not self._coincide(TokenType.TIPO):
            return None
        tipo = self._avanzar().valor
        id_tok = self._consumir(TokenType.IDENTIFICADOR, "identificador")
        if self._coincide(TokenType.PARENTESIS_ABRE):
            return self._def_func(tipo, id_tok.valor)
        else:
            return self._def_var(tipo, id_tok.valor)

    def _def_var(self, tipo: str, primer_id: str) -> NodoArbol:
        ids = [primer_id]
        while self._coincide(TokenType.COMA):
            self._avanzar()
            ids.append(self._consumir(TokenType.IDENTIFICADOR, "identificador").valor)
        self._consumir(TokenType.PUNTO_COMA, "';'")
        hijos = [NodoArbol("Tipo", tipo)]
        for i in ids:
            hijos.append(NodoArbol("Identificador", i))
        return NodoArbol("DefVar", "", hijos)

    def _def_func(self, tipo: str, nombre: str) -> NodoArbol:
        self._consumir(TokenType.PARENTESIS_ABRE, "'('")
        params = self._parametros()
        self._consumir(TokenType.PARENTESIS_CIERRA, "')'")
        self._consumir(TokenType.LLAVE_ABRE, "'{'")
        sentencias = self._def_locales()
        self._consumir(TokenType.LLAVE_CIERRA, "'}'")
        hijos = [
            NodoArbol("Tipo", tipo),
            NodoArbol("Identificador", nombre),
            NodoArbol("Parametros", "", params),
            NodoArbol("Bloque", "", sentencias)
        ]
        return NodoArbol("DefFunc", "", hijos)

    def _parametros(self) -> List[NodoArbol]:
        params = []
        if self._coincide(TokenType.TIPO):
            while True:
                t = self._avanzar().valor
                id_p = self._consumir(TokenType.IDENTIFICADOR, "identificador").valor
                params.append(NodoArbol("Parametro", "", [
                    NodoArbol("Tipo", t),
                    NodoArbol("Identificador", id_p)
                ]))
                if not self._coincide(TokenType.COMA):
                    break
                self._avanzar()
        return params

    def _def_locales(self) -> List[NodoArbol]:
        sentencias = []
        while not self._coincide(TokenType.LLAVE_CIERRA, TokenType.EOF):
            s = self._def_local()
            if s:
                sentencias.append(s)
        return sentencias

    def _def_local(self) -> Optional[NodoArbol]:
        if self._coincide(TokenType.TIPO):
            tipo = self._avanzar().valor
            id_tok = self._consumir(TokenType.IDENTIFICADOR, "identificador").valor
            ids = [id_tok]
            while self._coincide(TokenType.COMA):
                self._avanzar()
                ids.append(self._consumir(TokenType.IDENTIFICADOR, "identificador").valor)
            self._consumir(TokenType.PUNTO_COMA, "';'")
            hijos = [NodoArbol("Tipo", tipo)]
            for i in ids:
                hijos.append(NodoArbol("Identificador", i))
            return NodoArbol("DefVar", "", hijos)
        return self._sentencia()

    def _sentencia(self) -> Optional[NodoArbol]:
        if self._coincide(TokenType.IF):
            return self._sent_if()
        if self._coincide(TokenType.WHILE):
            return self._sent_while()
        if self._coincide(TokenType.RETURN):
            return self._sent_return()
        if self._coincide(TokenType.LLAVE_ABRE):
            return self._bloque()
        if self._coincide(TokenType.IDENTIFICADOR):
            return self._sent_asignacion_o_llamada()
        return None

    def _sent_if(self) -> NodoArbol:
        self._avanzar()
        self._consumir(TokenType.PARENTESIS_ABRE, "'('")
        cond = self._expresion()
        self._consumir(TokenType.PARENTESIS_CIERRA, "')'")
        body = self._sentencia()
        return NodoArbol("If", "", [
            NodoArbol("Condicion", "", [cond]),
            NodoArbol("Cuerpo", "", [body] if body else [])
        ])

    def _sent_while(self) -> NodoArbol:
        self._avanzar()
        self._consumir(TokenType.PARENTESIS_ABRE, "'('")
        cond = self._expresion()
        self._consumir(TokenType.PARENTESIS_CIERRA, "')'")
        body = self._sentencia()
        return NodoArbol("While", "", [
            NodoArbol("Condicion", "", [cond]),
            NodoArbol("Cuerpo", "", [body] if body else [])
        ])

    def _sent_return(self) -> NodoArbol:
        self._avanzar()
        if self._coincide(TokenType.PUNTO_COMA):
            self._avanzar()
            return NodoArbol("Return", "", [])
        exp = self._expresion()
        self._consumir(TokenType.PUNTO_COMA, "';'")
        return NodoArbol("Return", "", [exp])

    def _bloque(self) -> NodoArbol:
        self._consumir(TokenType.LLAVE_ABRE, "'{'")
        sentencias = []
        while not self._coincide(TokenType.LLAVE_CIERRA):
            s = self._sentencia()
            if s:
                sentencias.append(s)
        self._consumir(TokenType.LLAVE_CIERRA, "'}'")
        return NodoArbol("Bloque", "", sentencias)

    def _sent_asignacion_o_llamada(self) -> NodoArbol:
        id_tok = self._avanzar()
        if self._coincide(TokenType.ASIGNACION):
            self._avanzar()
            exp = self._expresion()
            self._consumir(TokenType.PUNTO_COMA, "';'")
            return NodoArbol("Asignacion", id_tok.valor, [exp])
        if self._coincide(TokenType.PARENTESIS_ABRE):
            args = self._argumentos()
            self._consumir(TokenType.PUNTO_COMA, "';'")
            return NodoArbol("LlamadaFunc", id_tok.valor, args)
        return NodoArbol("Identificador", id_tok.valor, [])

    def _argumentos(self) -> List[NodoArbol]:
        self._consumir(TokenType.PARENTESIS_ABRE, "'('")
        args = []
        if not self._coincide(TokenType.PARENTESIS_CIERRA):
            args.append(self._expresion())
            while self._coincide(TokenType.COMA):
                self._avanzar()
                args.append(self._expresion())
        self._consumir(TokenType.PARENTESIS_CIERRA, "')'")
        return args

    def _expresion(self) -> NodoArbol:
        return self._exp_or()

    def _exp_or(self) -> NodoArbol:
        izq = self._exp_and()
        while self._coincide(TokenType.OP_OR):
            op = self._avanzar().valor
            der = self._exp_and()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_and(self) -> NodoArbol:
        izq = self._exp_igualdad()
        while self._coincide(TokenType.OP_AND):
            op = self._avanzar().valor
            der = self._exp_igualdad()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_igualdad(self) -> NodoArbol:
        izq = self._exp_relacion()
        while self._coincide(TokenType.OP_IGUALDAD):
            op = self._avanzar().valor
            der = self._exp_relacion()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_relacion(self) -> NodoArbol:
        izq = self._exp_aditiva()
        while self._coincide(TokenType.OP_RELAC):
            op = self._avanzar().valor
            der = self._exp_aditiva()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_aditiva(self) -> NodoArbol:
        izq = self._exp_multiplicativa()
        while self._coincide(TokenType.OP_SUMA):
            op = self._avanzar().valor
            der = self._exp_multiplicativa()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_multiplicativa(self) -> NodoArbol:
        izq = self._exp_unaria()
        while self._coincide(TokenType.OP_MUL):
            op = self._avanzar().valor
            der = self._exp_unaria()
            izq = NodoArbol("OpBinaria", op, [izq, der])
        return izq

    def _exp_unaria(self) -> NodoArbol:
        if self._coincide(TokenType.OP_NOT):
            self._avanzar()
            return NodoArbol("OpUnaria", "!", [self._exp_unaria()])
        if self._coincide(TokenType.OP_SUMA) and self._actual().valor == '-':
            self._avanzar()
            return NodoArbol("OpUnaria", "-", [self._exp_unaria()])
        return self._exp_primaria()

    def _exp_primaria(self) -> NodoArbol:
        if self._coincide(TokenType.IDENTIFICADOR):
            id_tok = self._avanzar()
            if self._coincide(TokenType.PARENTESIS_ABRE):
                args = self._argumentos()
                return NodoArbol("LlamadaFunc", id_tok.valor, args)
            return NodoArbol("Identificador", id_tok.valor, [])
        if self._coincide(TokenType.ENTERO, TokenType.REAL):
            t = self._avanzar()
            return NodoArbol("Literal", t.valor, [])
        if self._coincide(TokenType.CADENA):
            t = self._avanzar()
            return NodoArbol("Cadena", t.valor, [])
        if self._coincide(TokenType.PARENTESIS_ABRE):
            self._avanzar()
            exp = self._expresion()
            self._consumir(TokenType.PARENTESIS_CIERRA, "')'")
            return exp
        return NodoArbol("Literal", "0", [])

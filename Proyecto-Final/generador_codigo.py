"""
Generación de código intermedio (tres direcciones / cuádruplas en texto).
Recorre el AST después del análisis semántico correcto.
"""

from typing import Dict, List, Optional, Set

from arbol_sintactico import NodoArbol


class GeneradorCodigo:
    """Emite líneas de código intermedio legible (estilo IC para compiladores)."""

    def __init__(self) -> None:
        self.lineas: List[str] = []
        self._temp = 0
        self._lbl = 0
        self._fun: Optional[str] = None
        self._env: Dict[str, str] = {}
        self._globales: Set[str] = set()

    def generar(self, raiz: NodoArbol) -> str:
        self.lineas = []
        self._temp = 0
        self._lbl = 0
        self._globales = self._recolectar_globales(raiz)
        self._emitir("# --- Variables globales ---")
        for g in sorted(self._globales):
            self._emitir(f"DECL_GLOBAL g_{g}")
        self._emitir("")
        for hijo in raiz.hijos:
            if hijo.tipo == "DefFunc":
                self._generar_funcion(hijo)
        return "\n".join(self.lineas)

    def _nueva_temp(self) -> str:
        t = f"t{self._temp}"
        self._temp += 1
        return t

    def _nueva_etiqueta(self, prefijo: str) -> str:
        lab = f"L_{prefijo}_{self._lbl}"
        self._lbl += 1
        return lab

    def _emitir(self, s: str) -> None:
        self.lineas.append(s)

    def _recolectar_globales(self, raiz: NodoArbol) -> Set[str]:
        g: Set[str] = set()
        if raiz.tipo != "Programa":
            return g
        for hijo in raiz.hijos:
            if hijo.tipo != "DefVar":
                continue
            for h in hijo.hijos[1:]:
                if h.tipo == "Identificador":
                    g.add(h.valor)
        return g

    def _lugar_ident(self, nombre: str) -> str:
        if nombre in self._env:
            return self._env[nombre]
        if nombre in self._globales:
            return f"g_{nombre}"
        return nombre

    def _generar_funcion(self, nodo: NodoArbol) -> None:
        tipo_ret = nodo.hijos[0].valor
        nombre = nodo.hijos[1].valor
        params_n = nodo.hijos[2]
        cuerpo = nodo.hijos[3]

        self._fun = nombre
        self._env = {}
        for p in params_n.hijos:
            if p.tipo != "Parametro":
                continue
            idp = p.hijos[1].valor
            self._env[idp] = f"{nombre}_{idp}"

        self._emitir(f"# función {nombre} -> {tipo_ret}")
        self._emitir(f"FUNC {nombre}")
        self._generar_bloque(cuerpo)
        self._emitir(f"END_FUNC {nombre}")
        self._emitir("")

    def _generar_bloque(self, nodo: NodoArbol) -> None:
        for s in nodo.hijos:
            self._generar_sentencia(s)

    def _generar_sentencia(self, s: NodoArbol) -> None:
        if s.tipo == "DefVar":
            tipo = s.hijos[0].valor
            for h in s.hijos[1:]:
                if h.tipo != "Identificador":
                    continue
                nombre = h.valor
                lugar = f"{self._fun}_{nombre}"
                self._env[nombre] = lugar
                self._emitir(f"DECL_LOCAL {lugar}  # {tipo}")
        elif s.tipo == "Asignacion":
            destino = self._lugar_ident(s.valor)
            src = self._generar_expresion(s.hijos[0])
            self._emitir(f"{destino} = {src}")
        elif s.tipo == "Return":
            if not s.hijos:
                self._emitir("RETURN_VOID")
            else:
                t = self._generar_expresion(s.hijos[0])
                self._emitir(f"RETURN {t}")
        elif s.tipo == "LlamadaFunc":
            self._generar_llamada(s, usar_resultado=False)
        elif s.tipo == "Bloque":
            self._generar_bloque(s)
        elif s.tipo == "If":
            self._generar_if(s)
        elif s.tipo == "While":
            self._generar_while(s)

    def _generar_if(self, nodo: NodoArbol) -> None:
        cond = nodo.hijos[0].hijos[0]
        cuerpo_n = nodo.hijos[1]
        t_cond = self._generar_expresion(cond)
        l_fin = self._nueva_etiqueta("if_end")
        self._emitir(f"IF_FALSE {t_cond} GOTO {l_fin}")
        if cuerpo_n.hijos:
            self._generar_sentencia(cuerpo_n.hijos[0])
        self._emitir(f"LABEL {l_fin}")

    def _generar_while(self, nodo: NodoArbol) -> None:
        cond = nodo.hijos[0].hijos[0]
        cuerpo_n = nodo.hijos[1]
        l_ini = self._nueva_etiqueta("while_start")
        l_fin = self._nueva_etiqueta("while_end")
        self._emitir(f"LABEL {l_ini}")
        t_cond = self._generar_expresion(cond)
        self._emitir(f"IF_FALSE {t_cond} GOTO {l_fin}")
        if cuerpo_n.hijos:
            self._generar_sentencia(cuerpo_n.hijos[0])
        self._emitir(f"GOTO {l_ini}")
        self._emitir(f"LABEL {l_fin}")

    def _generar_llamada(self, nodo: NodoArbol, usar_resultado: bool) -> str:
        nombre = nodo.valor
        temps: List[str] = []
        for arg in nodo.hijos:
            temps.append(self._generar_expresion(arg))
        args_str = ", ".join(temps)
        if usar_resultado:
            t = self._nueva_temp()
            self._emitir(f"{t} = CALL {nombre}({args_str})")
            return t
        self._emitir(f"CALL_VOID {nombre}({args_str})")
        return ""

    def _generar_expresion(self, n: NodoArbol) -> str:
        if n.tipo == "Literal":
            return n.valor
        if n.tipo == "Identificador":
            return self._lugar_ident(n.valor)
        if n.tipo == "Cadena":
            return repr(n.valor)
        if n.tipo == "LlamadaFunc":
            return self._generar_llamada(n, usar_resultado=True)
        if n.tipo == "OpUnaria":
            op = n.valor
            inner = self._generar_expresion(n.hijos[0])
            t = self._nueva_temp()
            if op == "-":
                self._emitir(f"{t} = NEG {inner}")
            elif op == "!":
                self._emitir(f"{t} = NOT {inner}")
            else:
                self._emitir(f"{t} = {op} {inner}")
            return t
        if n.tipo == "OpBinaria":
            izq = self._generar_expresion(n.hijos[0])
            der = self._generar_expresion(n.hijos[1])
            op = n.valor
            t = self._nueva_temp()
            if op in ("&&", "||"):
                self._emitir(f"{t} = {izq} {op} {der}")
            else:
                self._emitir(f"{t} = {izq} {op} {der}")
            return t
        t = self._nueva_temp()
        self._emitir(f"{t} = 0  # expresión no reconocida")
        return t

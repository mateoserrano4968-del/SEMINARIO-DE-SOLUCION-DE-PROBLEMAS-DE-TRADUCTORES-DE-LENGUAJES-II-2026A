"""
Analizador semántico: tabla de símbolos, comprobación de tipos,
llamadas a función y return.
"""

from typing import Dict, List, Optional, Tuple
from arbol_sintactico import NodoArbol


def tipo_a_char(tipo_str: str) -> str:
    t = tipo_str.lower()
    if t == "int":
        return "i"
    if t == "float":
        return "f"
    if t == "void":
        return "v"
    return "v"


def tipo_literal_desde_texto(val: str) -> str:
    """Literal numérico: entero 'i', real 'f'."""
    if "." in val:
        return "f"
    return "i"


class SimboloFuncion:
    def __init__(self, nombre: str, tipo_retorno: str, tipos_params: List[str]):
        self.nombre = nombre
        self.tipo_retorno = tipo_retorno
        self.tipos_params = tipos_params  # lista de 'i','f'


class AnalizadorSemantico:
    def __init__(self):
        self.errores: List[str] = []
        # globales: nombre -> ('var', tipo) o SimboloFuncion
        self.globales: Dict[str, object] = {}
        self.locales: Dict[str, str] = {}  # nombre -> tipo en función actual
        self.ambito_funcion: Optional[str] = None
        self.tipo_retorno_actual: str = "v"
        self._linea_aprox = 1

    def analizar(self, raiz: NodoArbol) -> Tuple[List[str], str]:
        self.errores = []
        self.globales = {}
        if raiz.tipo != "Programa":
            self.errores.append("Se esperaba nodo Programa")
            return self.errores, self._tabla_a_texto()

        # Primera pasada: registrar variables globales y firmas de funciones
        for hijo in raiz.hijos:
            if hijo.tipo == "DefVar":
                self._registrar_def_var_global(hijo)
            elif hijo.tipo == "DefFunc":
                self._registrar_firma_funcion(hijo)

        # Segunda pasada: cuerpos de funciones y validar globales ya listas
        for hijo in raiz.hijos:
            if hijo.tipo == "DefFunc":
                self._visitar_funcion(hijo)

        return self.errores, self._tabla_a_texto()

    def _registrar_def_var_global(self, nodo: NodoArbol) -> None:
        tipo_n = nodo.hijos[0]
        tipo = tipo_a_char(tipo_n.valor)
        for h in nodo.hijos[1:]:
            if h.tipo != "Identificador":
                continue
            nombre = h.valor
            if nombre in self.globales:
                ex = self.globales[nombre]
                if isinstance(ex, tuple) and ex[0] == "var":
                    self.errores.append(
                        f'Error semántico: variable global "{nombre}" redefinida'
                    )
                else:
                    self.errores.append(
                        f'Error semántico: nombre "{nombre}" ya está usado como función'
                    )
            else:
                self.globales[nombre] = ("var", tipo)

    def _registrar_firma_funcion(self, nodo: NodoArbol) -> None:
        tipo_ret = tipo_a_char(nodo.hijos[0].valor)
        nombre = nodo.hijos[1].valor
        params_n = nodo.hijos[2]
        tipos_p: List[str] = []
        nombres_p: List[str] = []
        for p in params_n.hijos:
            if p.tipo != "Parametro":
                continue
            tp = tipo_a_char(p.hijos[0].valor)
            idp = p.hijos[1].valor
            tipos_p.append(tp)
            if idp in nombres_p:
                self.errores.append(
                    f'Error semántico: parámetro "{idp}" redefinido en "{nombre}"'
                )
            nombres_p.append(idp)

        if nombre in self.globales:
            ex = self.globales[nombre]
            if isinstance(ex, SimboloFuncion):
                self.errores.append(f'Error semántico: función "{nombre}" redefinida')
            else:
                self.errores.append(
                    f'Error semántico: nombre "{nombre}" ya está usado como variable global'
                )
        else:
            self.globales[nombre] = SimboloFuncion(nombre, tipo_ret, tipos_p)

    def _visitar_funcion(self, nodo: NodoArbol) -> None:
        nombre_fun = nodo.hijos[1].valor
        sim = self.globales.get(nombre_fun)
        if not isinstance(sim, SimboloFuncion):
            return
        self.ambito_funcion = nombre_fun
        self.tipo_retorno_actual = sim.tipo_retorno
        self.locales = {}

        params_n = nodo.hijos[2]
        for p in params_n.hijos:
            if p.tipo != "Parametro":
                continue
            tp = tipo_a_char(p.hijos[0].valor)
            idp = p.hijos[1].valor
            if idp in self.locales:
                self.errores.append(
                    f'Error semántico: variable local "{idp}" redefinida'
                )
            self.locales[idp] = tp

        bloque = nodo.hijos[3]
        self._visitar_bloque(bloque)

        self.ambito_funcion = None
        self.locales = {}

    def _visitar_bloque(self, nodo: NodoArbol) -> None:
        for s in nodo.hijos:
            self._visitar_sentencia(s)

    def _visitar_sentencia(self, s: NodoArbol) -> None:
        if s.tipo == "DefVar":
            self._registrar_def_var_local(s)
        elif s.tipo == "Asignacion":
            self._visitar_asignacion(s)
        elif s.tipo == "Return":
            self._visitar_return(s)
        elif s.tipo == "LlamadaFunc":
            self._visitar_llamada_stmt(s)
        elif s.tipo == "Bloque":
            self._visitar_bloque(s)
        elif s.tipo == "If":
            self._visitar_if(s)
        elif s.tipo == "While":
            self._visitar_while(s)

    def _visitar_if(self, nodo: NodoArbol) -> None:
        cond = nodo.hijos[0].hijos[0]
        self._tipo_expresion(cond)
        cuerpo = nodo.hijos[1]
        if cuerpo.hijos:
            self._visitar_sentencia(cuerpo.hijos[0])

    def _visitar_while(self, nodo: NodoArbol) -> None:
        cond = nodo.hijos[0].hijos[0]
        self._tipo_expresion(cond)
        cuerpo = nodo.hijos[1]
        if cuerpo.hijos:
            self._visitar_sentencia(cuerpo.hijos[0])

    def _registrar_def_var_local(self, nodo: NodoArbol) -> None:
        tipo = tipo_a_char(nodo.hijos[0].valor)
        for h in nodo.hijos[1:]:
            if h.tipo != "Identificador":
                continue
            nombre = h.valor
            if nombre in self.locales:
                self.errores.append(
                    f'Error semántico: variable local "{nombre}" redefinida'
                )
            self.locales[nombre] = tipo

    def _tipo_ident(self, nombre: str) -> Optional[str]:
        if nombre in self.locales:
            return self.locales[nombre]
        if nombre in self.globales:
            g = self.globales[nombre]
            if isinstance(g, tuple) and g[0] == "var":
                return g[1]
        self.errores.append(
            f'Error semántico: identificador "{nombre}" no declarado'
        )
        return None

    def _visitar_asignacion(self, nodo: NodoArbol) -> None:
        var = nodo.valor
        t_var = self._tipo_ident(var)
        if t_var is None:
            return
        exp_t = self._tipo_expresion(nodo.hijos[0])
        if exp_t is None:
            return
        if t_var != exp_t:
            self.errores.append(
                f'Error semántico: tipos incompatibles en asignación a "{var}" '
                f"(se esperaba tipo '{t_var}', expresión tipo '{exp_t}')"
            )

    def _visitar_return(self, nodo: NodoArbol) -> None:
        if not nodo.hijos:
            if self.tipo_retorno_actual != "v":
                self.errores.append(
                    "Error semántico: return sin expresión en función no void"
                )
            return
        t = self._tipo_expresion(nodo.hijos[0])
        if t is None:
            return
        if t != self.tipo_retorno_actual:
            self.errores.append(
                f"Error semántico: tipo de return incompatible "
                f"(función retorna '{self.tipo_retorno_actual}', expresión '{t}')"
            )

    def _visitar_llamada_stmt(self, nodo: NodoArbol) -> None:
        self._validar_llamada(nodo)

    def _validar_llamada(self, nodo: NodoArbol) -> Optional[str]:
        nombre = nodo.valor
        sim = self.globales.get(nombre)
        if sim is None:
            self.errores.append(
                f'Error semántico: función "{nombre}" no declarada'
            )
            return None
        if isinstance(sim, tuple):
            self.errores.append(
                f'Error semántico: "{nombre}" es variable, no función'
            )
            return None
        if not isinstance(sim, SimboloFuncion):
            return None
        args = nodo.hijos
        if len(args) != len(sim.tipos_params):
            self.errores.append(
                f'Error semántico: número de argumentos incorrecto en "{nombre}" '
                f"(esperados {len(sim.tipos_params)}, dados {len(args)})"
            )
            return sim.tipo_retorno
        for i, (arg_n, esperado) in enumerate(zip(args, sim.tipos_params)):
            obtenido = self._tipo_expresion(arg_n)
            if obtenido is None:
                continue
            if obtenido != esperado:
                self.errores.append(
                    f'Error semántico: argumento {i + 1} de "{nombre}" incompatible '
                    f"(se esperaba '{esperado}', se obtuvo '{obtenido}')"
                )
        return sim.tipo_retorno

    def _tipo_expresion(self, nodo: NodoArbol) -> Optional[str]:
        if nodo.tipo == "Identificador":
            return self._tipo_ident(nodo.valor)
        if nodo.tipo == "Literal":
            return tipo_literal_desde_texto(nodo.valor)
        if nodo.tipo == "Cadena":
            return "s"
        if nodo.tipo == "LlamadaFunc":
            return self._validar_llamada(nodo)
        if nodo.tipo == "OpBinaria":
            op = nodo.valor
            if op in ("+", "-", "*", "/"):
                izq = self._tipo_expresion(nodo.hijos[0])
                der = self._tipo_expresion(nodo.hijos[1])
                if izq is None or der is None:
                    return None
                if op in ("*", "/"):
                    if izq == "f" or der == "f":
                        return "f"
                    return "i"
                # + -
                if izq == "f" or der == "f":
                    return "f"
                return "i"
            # lógicos / relacional: simplificado
            return "i"
        if nodo.tipo == "OpUnaria":
            return self._tipo_expresion(nodo.hijos[0])
        return None

    def _tabla_a_texto(self) -> str:
        lineas = ["", "*** Tabla de símbolos (resumen) ***", ""]
        for nombre, sim in sorted(self.globales.items()):
            if isinstance(sim, tuple) and sim[0] == "var":
                lineas.append(f"  Variable global: {nombre}  tipo={sim[1]}")
            elif isinstance(sim, SimboloFuncion):
                lineas.append(
                    f"  Función: {nombre}  retorno={sim.tipo_retorno}  "
                    f"params={''.join(sim.tipos_params)}"
                )
        lineas.append("")
        return "\n".join(lineas)

"""
Cargador de la gramática del compilador (Modulo4).
Carga las tablas LR desde compilador.csv y las producciones desde compilador.inf
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Ruta base de la gramática
DIR_GRAMATICA = Path(__file__).parent / "GramaticaCompilador"


class Produccion:
    """Representa una producción: LHS -> RHS"""

    def __init__(self, numero: int, lhs: str, rhs: List[str]):
        self.numero = numero
        self.lhs = lhs
        self.rhs = rhs
        self.longitud = len(rhs)

    def __repr__(self) -> str:
        rhs_str = " ".join(self.rhs) if self.rhs else "ε"
        return f"R{self.numero}: {self.lhs} -> {rhs_str}"


def cargar_gramatica() -> Tuple[Dict[str, Dict[str, str]], List[Produccion], List[str]]:
    """
    Carga la tabla LR desde CSV y las producciones desde compilador.inf
    Retorna: (tabla_acciones, producciones, nombres_simbolos)
    """
    csv_path = DIR_GRAMATICA / "compilador.csv"
    inf_path = DIR_GRAMATICA / "compilador.inf"

    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró la tabla LR: {csv_path}")

    # Cargar nombres de símbolos desde la cabecera del CSV
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        nombres_simbolos = [h.strip() for h in headers[1:] if h.strip()]

    # Cargar tabla LR (dN=shift, rN=reduce, números=GOTO)
    tabla: Dict[str, Dict[str, str]] = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            estado = row[0].strip()
            tabla[estado] = {}
            for i, valor in enumerate(row[1:], start=0):
                if i < len(nombres_simbolos) and valor.strip():
                    simbolo = nombres_simbolos[i]
                    tabla[estado][simbolo] = valor.strip()

    # Cargar producciones desde compilador.inf (R1-R52)
    producciones = _cargar_producciones_inf(inf_path)

    if not producciones:
        producciones = _producciones_por_defecto()

    return tabla, producciones, nombres_simbolos


def _cargar_producciones_inf(ruta: Path) -> List[Produccion]:
    """
    Carga las producciones desde compilador.inf
    Formato: R1 <LHS> ::= <RHS1> <RHS2> ... | \\e para epsilon
    """
    producciones: List[Produccion] = []

    if not ruta.exists():
        return producciones

    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            match = re.match(r"R(\d+)\s+<(\w+)>\s*::=\s*(.+)", linea)
            if not match:
                continue

            num_regla = int(match.group(1))
            lhs = match.group(2)
            rhs_str = match.group(3).strip()

            if rhs_str == r"\e":
                rhs = []
            else:
                rhs = _parsear_rhs(rhs_str)

            prod = Produccion(num_regla - 1, lhs, rhs)
            producciones.append(prod)

    producciones.sort(key=lambda p: p.numero)
    return producciones


def _parsear_rhs(rhs_str: str) -> List[str]:
    """Parsea el lado derecho"""
    resultado = []
    tokens = re.findall(r"<(\w+)>|([^\s<]+)", rhs_str)
    for g1, g2 in tokens:
        if g1:
            resultado.append(g1)
        elif g2 and g2 not in (r"\e", ""):
            resultado.append(g2.strip())
    return resultado


def _producciones_por_defecto() -> List[Produccion]:
    """Producciones de la gramática del compilador (fallback)"""
    return [
        Produccion(0, "programa", ["Definiciones"]),
        Produccion(1, "Definiciones", []),
        Produccion(2, "Definiciones", ["Definicion", "Definiciones"]),
        Produccion(3, "Definicion", ["DefVar"]),
        Produccion(4, "Definicion", ["DefFunc"]),
        Produccion(5, "DefVar", ["tipo", "identificador", "ListaVar", ";"]),
        Produccion(6, "ListaVar", []),
        Produccion(7, "ListaVar", [",", "identificador", "ListaVar"]),
        Produccion(8, "DefFunc", ["tipo", "identificador", "(", "Parametros", ")", "BloqFunc"]),
        Produccion(9, "Parametros", []),
        Produccion(10, "Parametros", ["tipo", "identificador", "ListaParam"]),
        Produccion(11, "ListaParam", []),
        Produccion(12, "ListaParam", [",", "tipo", "identificador", "ListaParam"]),
        Produccion(13, "BloqFunc", ["{", "DefLocales", "}"]),
    ]

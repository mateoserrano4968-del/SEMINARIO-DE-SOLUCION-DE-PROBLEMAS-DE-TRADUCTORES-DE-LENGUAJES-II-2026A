"""Carga tablas LR y producciones desde compilador.csv y compilador.inf."""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

DIR_GRAMATICA = Path(__file__).parent / "GramaticaCompilador"


class Produccion:
    def __init__(self, numero: int, lhs: str, rhs: List[str]):
        self.numero = numero
        self.lhs = lhs
        self.rhs = rhs
        self.longitud = len(rhs)


def cargar_gramatica() -> Tuple[Dict[str, Dict[str, str]], List[Produccion], List[str]]:
    csv_path = DIR_GRAMATICA / "compilador.csv"
    inf_path = DIR_GRAMATICA / "compilador.inf"

    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró: {csv_path}")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        nombres = [h.strip() for h in headers[1:] if h.strip()]

    tabla: Dict[str, Dict[str, str]] = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            estado = row[0].strip()
            tabla[estado] = {}
            for i, v in enumerate(row[1:], 0):
                if i < len(nombres) and v.strip():
                    tabla[estado][nombres[i]] = v.strip()

    producciones: List[Produccion] = []
    if inf_path.exists():
        with open(inf_path, encoding="utf-8") as f:
            for linea in f:
                m = re.match(r"R(\d+)\s+<(\w+)>\s*::=\s*(.+)", linea.strip())
                if not m:
                    continue
                num, lhs, rhs_str = int(m.group(1)), m.group(2), m.group(3).strip()
                if rhs_str == r"\e":
                    rhs = []
                else:
                    rhs = []
                    for g1, g2 in re.findall(r"<(\w+)>|([^\s<]+)", rhs_str):
                        if g1:
                            rhs.append(g1)
                        elif g2 and g2 not in (r"\e", ""):
                            rhs.append(g2.strip())
                producciones.append(Produccion(num - 1, lhs, rhs))
        producciones.sort(key=lambda p: p.numero)

    if not producciones:
        producciones = [
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
        ]

    return tabla, producciones, nombres

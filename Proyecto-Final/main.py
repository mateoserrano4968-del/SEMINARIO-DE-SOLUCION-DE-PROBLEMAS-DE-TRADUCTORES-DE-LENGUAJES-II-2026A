"""
Compilador — Proyecto final (Traductores II)
Pipeline: léxico → sintáctico (AST) → semántico → generación de código intermedio.
"""

import argparse
import sys
import traceback
from pathlib import Path

from analizador_lexico import AnalizadorLexico
from analizador_semantico import AnalizadorSemantico
from generador_codigo import GeneradorCodigo
from parser_arbol import ParserArbol

_DIR_SCRIPT = Path(__file__).resolve().parent


def _resolver_ruta(entrada: str) -> Path:
    s = entrada.strip().strip('"').strip("'")
    if not s:
        return Path("")
    p = Path(s)
    if p.is_file():
        return p.resolve()
    for base in (Path.cwd(), _DIR_SCRIPT):
        try:
            candidato = (base / p).resolve()
        except OSError:
            continue
        if candidato.is_file():
            return candidato
    return p


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Compilador (léxico, sintáctico, semántico, código intermedio)"
    )
    ap.add_argument(
        "archivo",
        nargs="?",
        help="Archivo fuente .txt (si se omite, se pide por consola)",
    )
    ap.add_argument(
        "--arbol",
        action="store_true",
        help="Imprime el árbol sintáctico si el análisis llegó a construirlo.",
    )
    args = ap.parse_args()

    print("=" * 60)
    print("  Proyecto final — Compilador (subconjunto tipo C)")
    print("=" * 60)

    if args.archivo:
        ruta = _resolver_ruta(args.archivo)
    else:
        entrada = input("\nArchivo de entrada (ej. ejemplo_ok.txt): ").strip()
        if not entrada:
            print("No se especificó archivo.")
            return
        ruta = _resolver_ruta(entrada)

    if not ruta.exists() or not ruta.is_file():
        print(f"\nError: No se encontró el archivo '{ruta}'")
        print(f"  Carpeta del programa: {_DIR_SCRIPT}")
        print("  Sugerencia: pon el .txt en esa carpeta o usa ruta completa.")
        return

    codigo = ruta.read_text(encoding="utf-8")
    print(f"\n--- Código fuente: {ruta} ---\n")
    print(codigo)
    print("\n" + "-" * 60)

    print("\n[1] Analizador léxico")
    lexico = AnalizadorLexico(codigo)
    tokens = lexico.analizar()
    if lexico.tiene_errores():
        print("\n*** ERRORES LÉXICOS ***")
        for e in lexico.errores:
            print(f"  {e}")
        return

    print(f"  Tokens generados: {len(tokens) - 1} (+ EOF)")

    print("\n[2] Analizador sintáctico (AST)")
    parser = ParserArbol(tokens)
    arbol = parser.parsear()
    if arbol is None or parser.errores:
        print("\n*** ERRORES SINTÁCTICOS ***")
        for e in parser.errores:
            print(f"  {e}")
        return

    print("  AST construido correctamente.")
    if args.arbol:
        print("\n*** Árbol sintáctico ***\n")
        print(arbol.mostrar())

    print("\n[3] Analizador semántico")
    sem = AnalizadorSemantico()
    errores, tabla = sem.analizar(arbol)
    print(tabla)
    if errores:
        print("\n*** ERRORES SEMÁNTICOS ***")
        for e in errores:
            print(f"  {e}")
        print("\n(No se genera código intermedio si hay errores semánticos.)")
        print("=" * 60)
        return

    print("  Sin errores semánticos.")

    print("\n[4] Generación de código (intermedio)")
    gen = GeneradorCodigo()
    intermedio = gen.generar(arbol)
    print("\n*** Código intermedio ***\n")
    print(intermedio)
    print("=" * 60)


def _pausa_si_consola() -> None:
    try:
        if sys.stdin.isatty():
            input("\nPresiona Enter para salir...")
    except (EOFError, OSError):
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n*** Error inesperado ***")
        traceback.print_exc()
    finally:
        if len(sys.argv) <= 1:
            _pausa_si_consola()

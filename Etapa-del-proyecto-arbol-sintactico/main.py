"""
Etapa: Árbol Sintáctico
Genera y muestra el árbol sintáctico del código fuente.
"""

import sys
from pathlib import Path
from analizador_lexico import AnalizadorLexico
from parser_arbol import ParserArbol


def main():
    print("=" * 60)
    print("  Etapa: Árbol Sintáctico")
    print("=" * 60)

    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        entrada = input("\nArchivo de entrada: ").strip()
        if not entrada:
            print("No se especificó archivo.")
            return
        ruta = Path(entrada)

    if not ruta.exists():
        print(f"\nError: No se encontró '{ruta}'")
        return

    codigo = ruta.read_text(encoding="utf-8")
    print(f"\n--- Código fuente: {ruta} ---\n")
    print(codigo)
    print("\n" + "-" * 60)

    lexico = AnalizadorLexico(codigo)
    tokens = lexico.analizar()

    if lexico.tiene_errores():
        print("\n*** ERRORES LÉXICOS ***")
        for e in lexico.errores:
            print(f"  {e}")
        return

    parser = ParserArbol(tokens)
    arbol = parser.parsear()

    if arbol is None or parser.errores:
        print("\n*** ERRORES SINTÁCTICOS ***")
        for e in parser.errores:
            print(f"  {e}")
        return

    print("\n*** ÁRBOL SINTÁCTICO ***\n")
    print(arbol.mostrar())
    print("=" * 60)


if __name__ == "__main__":
    main()

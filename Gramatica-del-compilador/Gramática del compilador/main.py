"""Compilador - Analizador Léxico + Sintáctico LR. Gramática Modulo4."""

import sys
from pathlib import Path

from analizador_lexico import AnalizadorLexico
from analizador_sintactico_lr import AnalizadorSintacticoLR
from tokens import TokenType


def main():
    print("=" * 60)
    print("  Gramática del compilador")
    print("  Analizador Léxico + Tablas LR (Modulo4)")
    print("=" * 60)

    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(input("\nArchivo de entrada: ").strip())
    if not ruta or not ruta.exists():
        print("Error: archivo no encontrado.")
        return

    try:
        codigo = ruta.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error al leer: {e}")
        return

    if not codigo.strip():
        print("Archivo vacío.")
        return

    print(f"\nArchivo: {ruta}")
    print("-" * 60)
    print(codigo)
    print("-" * 60)

    lexico = AnalizadorLexico(codigo)
    tokens = lexico.analizar()

    if lexico.tiene_errores():
        print("\n*** ERRORES LÉXICOS ***")
        for e in lexico.errores:
            print(f"  {e}")
        return

    print("\nTOKENS RECONOCIDOS:")
    for t in tokens:
        if t.tipo != TokenType.EOF:
            print(f"  {t}")

    parser = AnalizadorSintacticoLR(tokens)
    ok = parser.analizar()

    if ok:
        print("\n*** ANÁLISIS SINTÁCTICO: CORRECTO ***")
    else:
        print("\n*** ERRORES SINTÁCTICOS ***")
        for e in parser.errores:
            print(f"  {e}")

    try:
        input("\nPresiona Enter para salir...")
    except EOFError:
        pass


if __name__ == "__main__":
    main()

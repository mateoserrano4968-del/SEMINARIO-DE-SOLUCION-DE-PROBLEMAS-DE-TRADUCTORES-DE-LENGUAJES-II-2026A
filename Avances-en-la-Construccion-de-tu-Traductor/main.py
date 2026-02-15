
import sys
from pathlib import Path

from analizador_lexico import AnalizadorLexico
from analizador_sintactico import AnalizadorSintactico
from tokens import TokenType


def imprimir_tokens(tokens: list) -> None:
    print("\n" + "=" * 60)
    print("TOKENS RECONOCIDOS")
    print("=" * 60)
    print(f"{'Tipo':<22} {'Valor':<15} {'Línea':<8} {'Columna':<8}")
    print("-" * 60)
    for token in tokens:
        if token.tipo != TokenType.EOF:
            print(f"{token.tipo.name:<22} {token.valor!r:<15} {token.linea:<8} {token.columna:<8}")
    print(f"{'EOF':<22} {'$':<15} {'-':<8} {'-':<8}")
    print("=" * 60)
    print(f"Total: {len(tokens)} tokens\n")


def main() -> None:
    print("=" * 60)
    print("  Avances en la Construcción de tu Traductor")
    print("  Análisis Léxico y Sintáctico")
    print("=" * 60)

    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        entrada = input("\nArchivo de entrada: ").strip()
        if not entrada:
            print("No se especificó archivo.")
            input("Presiona Enter para salir...")
            return
        ruta = Path(entrada)

    if not ruta.exists():
        print(f"\nError: No se encontró el archivo '{ruta.absolute()}'")
        input("Presiona Enter para salir...")
        return

    try:
        codigo = ruta.read_text(encoding="utf-8")
    except Exception as e:
        print(f"\nError al leer el archivo: {e}")
        input("Presiona Enter para salir...")
        return

    if not codigo.strip():
        print("\nEl archivo está vacío.")
        input("Presiona Enter para salir...")
        return

    print(f"\nArchivo: {ruta}")
    print("-" * 60)
    print(codigo)
    print("-" * 60)

    lexico = AnalizadorLexico(codigo)
    tokens = lexico.analizar()

    if lexico.tiene_errores():
        print("\n*** ERRORES LÉXICOS ***")
        for err in lexico.errores:
            print(f"  {err}")
        print("\nNo se realiza análisis sintáctico debido a errores léxicos.")
        imprimir_tokens(tokens)
        return

    imprimir_tokens(tokens)

    sintactico = AnalizadorSintactico(tokens)
    try:
        ok = sintactico.analizar()
        if ok:
            print("*** ANÁLISIS SINTÁCTICO: CORRECTO ***")
        else:
            print("*** ERRORES SINTÁCTICOS ***")
            for err in sintactico.errores:
                print(f"  {err}")
    except Exception as e:
        print(f"*** Error durante análisis sintáctico: {e} ***")

    try:
        input("\nPresiona Enter para salir...")
    except EOFError:
        pass


if __name__ == "__main__":
    main()

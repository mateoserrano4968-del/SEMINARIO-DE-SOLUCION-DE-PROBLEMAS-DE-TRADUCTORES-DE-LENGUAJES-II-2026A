"""
Etapa: Analizador semántico
Léxico → parser → validación semántica (tabla de símbolos y errores).
"""

import sys
import traceback
from pathlib import Path

from analizador_lexico import AnalizadorLexico
from parser_arbol import ParserArbol
from analizador_semantico import AnalizadorSemantico


# Carpeta donde está main.py (para encontrar ejemplo1.txt aunque el "directorio actual" sea otro)
_DIR_SCRIPT = Path(__file__).resolve().parent


def _resolver_ruta(entrada: str) -> Path:
    """Quita comillas y busca el archivo en cwd y en la carpeta de main.py."""
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


def main():
    print("=" * 60)
    print("  Etapa: Analizador semántico")
    print("=" * 60)

    if len(sys.argv) > 1:
        ruta = _resolver_ruta(sys.argv[1])
    else:
        entrada = input("\nArchivo de entrada (ej. ejemplo1.txt): ").strip()
        if not entrada:
            print("No se especificó archivo.")
            return
        ruta = _resolver_ruta(entrada)

    if not ruta.exists() or not ruta.is_file():
        print(f"\nError: No se encontró el archivo '{ruta}'")
        print(f"  Carpeta del programa: {_DIR_SCRIPT}")
        print("  Sugerencia: pon el .txt en esa carpeta o arrastra el archivo a la ventana.")
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

    sem = AnalizadorSemantico()
    errores, tabla = sem.analizar(arbol)

    print(tabla)

    if errores:
        print("*** ERRORES SEMÁNTICOS ***")
        for e in errores:
            print(f"  {e}")
    else:
        print("*** Sin errores semánticos ***")

    print("=" * 60)


def _pausa_si_consola():
    """En Windows, al hacer doble clic o escribir el nombre del archivo, el CMD se cierra sola."""
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
        # Solo pausa si no pasaste el archivo como argumento (python main.py archivo.txt)
        if len(sys.argv) <= 1:
            _pausa_si_consola()

# Salidas del Analizador

## Caso 1: Entrada correcta
`python main.py ejemplos/entrada_correcto.txt`
- Tokens reconocidos
- ANÁLISIS SINTÁCTICO: CORRECTO

## Caso 2: Error léxico (@ no reconocido)
`python main.py ejemplos/entrada_error_lexico.txt`
- ERRORES LÉXICOS
- No se realiza análisis sintáctico

## Caso 3: Error sintáctico (falta ;)
`python main.py ejemplos/entrada_error_sintactico.txt`
- Tokens reconocidos
- ERRORES SINTÁCTICOS

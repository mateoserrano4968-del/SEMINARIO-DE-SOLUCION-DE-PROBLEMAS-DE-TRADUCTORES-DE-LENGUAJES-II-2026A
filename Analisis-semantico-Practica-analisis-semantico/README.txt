ANÁLISIS SEMÁNTICO - Práctica
Traductores de Lenguajes II
============================

DESCRIPCIÓN:
  Analizador semántico que valida tipos, tabla de símbolos y detecta
  errores como variables no definidas, redefiniciones y tipos incompatibles.

ARCHIVOS:
  - principal.cpp      : Punto de entrada y árboles de prueba
  - tablaSimbolos.cpp  : Implementación tabla de símbolos
  - tablaSimbolos.h    : Definición tabla de símbolos
  - arbolSintactico.h  : Árbol sintáctico y validación de tipos
  - Semantico.h       : Analizador semántico

COMPILAR Y EJECUTAR:
  Opción 1: Doble clic en compilar.bat
  
  Opción 2: En la terminal:
    g++ -o pract1_semV principal.cpp tablaSimbolos.cpp
    pract1_semV.exe

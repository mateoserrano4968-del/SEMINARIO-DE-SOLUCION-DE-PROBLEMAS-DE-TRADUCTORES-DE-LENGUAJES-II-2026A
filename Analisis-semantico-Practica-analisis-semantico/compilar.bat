@echo off
chcp 65001 >nul
echo Compilando...
g++ -o pract1_semV.exe principal.cpp tablaSimbolos.cpp
if %errorlevel% equ 0 (
    echo.
    echo Compilacion exitosa. Ejecutando...
    echo.
    pract1_semV.exe
    echo.
    pause
) else (
    echo.
    echo ERROR: g++ no encontrado. Instala MinGW o Visual Studio.
    pause
)

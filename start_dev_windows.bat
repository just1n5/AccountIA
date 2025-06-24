@echo off
REM AccountIA - Desarrollo para Windows
REM Script para iniciar servicios con encoding UTF-8

echo ================================
echo AccountIA - Modo Desarrollo
echo ================================

REM Configurar encoding UTF-8 para Python
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1
set PYTHONUTF8=1
set PYTHONLEGACYWINDOWSFS=1

REM Configurar console para UTF-8
chcp 65001 >nul 2>&1

echo [INFO] Configurado encoding UTF-8 para Python
echo [INFO] Variables configuradas:
echo   - PYTHONIOENCODING=%PYTHONIOENCODING%
echo   - PYTHONUTF8=%PYTHONUTF8%
echo.

echo [INIT] Iniciando servicios de desarrollo...
echo [INIT] Backend: http://localhost:8000
echo [INIT] Frontend: http://localhost:3000
echo.

REM Ejecutar desarrollo
npm run dev

echo.
echo [DONE] Servicios terminados
pause

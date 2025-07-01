@echo off
title AccountIA - Reparación Rápida Backend

echo.
echo 🚀 REPARACIÓN RÁPIDA - AccountIA Backend
echo =======================================

echo.
echo [1/4] 🐳 Iniciando servicios Docker...
call npm run docker:up

echo.
echo [2/4] ⏳ Esperando base de datos...
timeout /t 8 /nobreak >nul

echo.
echo [3/4] 🔧 Aplicando migraciones...
call npm run backend:migrate

echo.
echo [4/4] ✅ Verificación rápida...
echo Probando endpoint básico...
curl -s http://localhost:8000/health/ && echo ✅ Backend OK || echo ❌ Backend Error

echo.
echo 🎯 REPARACIÓN COMPLETADA
echo ========================
echo.
echo 💡 Próximos pasos:
echo    1. Refrescar el navegador (Ctrl+F5)
echo    2. Ir a: http://localhost:3000/dashboard
echo    3. Si hay errores: npm run logs:backend
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

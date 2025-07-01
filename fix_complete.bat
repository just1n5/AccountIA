@echo off
echo.
echo 🚀 REPARACIÓN COMPLETA ACCOUNTIA
echo ===============================

echo.
echo [1/3] 🔧 Corrigiendo configuración del frontend...

REM Backup del archivo original
if exist "frontend\src\services\api.ts" (
    copy "frontend\src\services\api.ts" "frontend\src\services\api_backup.ts" >nul
    echo ✅ Backup creado: api_backup.ts
)

REM Aplicar el fix
if exist "frontend\src\services\api_fixed.ts" (
    copy "frontend\src\services\api_fixed.ts" "frontend\src\services\api.ts" >nul
    echo ✅ Configuración API corregida
) else (
    echo ❌ Archivo de fix no encontrado
)

echo.
echo [2/3] 🐍 Iniciando backend...
cd backend

echo Aplicando migraciones...
python manage.py migrate || echo ❌ Error en migraciones

echo.
echo [3/3] 🚀 Iniciando servidor backend...
echo ================================
echo.
echo 📍 Backend URL: http://localhost:8000
echo 📍 Frontend URL: http://localhost:3000
echo.
echo 💡 Para el frontend ejecuta en otra terminal:
echo    cd frontend
echo    npm run dev
echo.
echo ⏹️  Para detener el backend: Ctrl+C
echo.

python manage.py runserver 8000

cd ..
echo.
echo ✅ Backend terminado
pause

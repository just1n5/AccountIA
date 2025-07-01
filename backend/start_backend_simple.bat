@echo off
echo 🔧 INICIANDO BACKEND SIMPLIFICADO PARA ACCOUNTIA
echo.

cd /d "C:\Users\justi\Desktop\Proyecto Accountia\backend"

echo 🔄 Configurando entorno...
set DJANGO_SETTINGS_MODULE=config.settings.development_simple

echo 🔄 Inicializando backend...
python init_backend.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error en la inicialización
    pause
    exit /b 1
)

echo.
echo 🚀 INICIANDO SERVIDOR DJANGO...
echo 🌐 Backend disponible en: http://localhost:8000
echo 📚 API docs en: http://localhost:8000/api/docs/
echo 🛑 Presiona Ctrl+C para detener
echo.

python manage.py runserver 0.0.0.0:8000 --settings=config.settings.development_simple

pause

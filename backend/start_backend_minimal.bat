@echo off
echo 🔧 INICIANDO BACKEND MÍNIMO PARA ACCOUNTIA
echo.

cd /d "C:\Users\justi\Desktop\Proyecto Accountia\backend"

echo 🔄 Configurando entorno mínimo...
set DJANGO_SETTINGS_MODULE=config.settings.development_minimal
set ROOT_URLCONF=config.urls_minimal

echo 🔄 Inicializando backend mínimo...
python init_backend_minimal.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error en la inicialización
    pause
    exit /b 1
)

echo.
echo 🚀 INICIANDO SERVIDOR DJANGO MÍNIMO...
echo 🌐 Backend disponible en: http://localhost:8000
echo 📚 API info en: http://localhost:8000/api/info/
echo 💡 Solo disponibles: declaraciones, usuarios, auth
echo 🛑 Presiona Ctrl+C para detener
echo.

python manage.py runserver 0.0.0.0:8000 --settings=config.settings.development_minimal

pause

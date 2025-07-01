@echo off
echo 🚀 Iniciando Backend AccountIA...
echo.

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv_clean\Scripts\activate

REM Verificar Django
echo 🔍 Verificando Django...
python -c "import django; print('✅ Django OK:', django.VERSION)" || goto :error

REM Aplicar migraciones si es necesario
echo 📋 Verificando migraciones...
python manage.py migrate --verbosity=0

REM Iniciar servidor
echo 🌐 Iniciando servidor en http://localhost:8000
echo ⏹️  Presiona Ctrl+C para detener
echo.
python manage.py runserver 0.0.0.0:8000

goto :end

:error
echo ❌ Error: No se pudo inicializar Django
echo 💡 Asegúrate de que el entorno virtual esté configurado correctamente
pause

:end

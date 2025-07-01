@echo off
echo 🚀 Iniciando Backend AccountIA con entorno virtual...

REM Cambiar al directorio backend
cd backend

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv_clean\Scripts\activate

REM Verificar Django
python -c "import django; print('✅ Django OK:', django.VERSION)" || goto :error

REM Iniciar servidor
echo 🌐 Iniciando servidor en http://localhost:8000
python manage.py runserver 0.0.0.0:8000

goto :end

:error
echo ❌ Error: No se pudo inicializar Django
echo 💡 Asegúrate de que el entorno virtual esté configurado correctamente
exit /b 1

:end
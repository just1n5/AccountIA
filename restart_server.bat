@echo off
echo ========================================
echo ACCOUNTIA - REINICIO DE SERVIDOR DJANGO
echo ========================================
echo.

echo Reiniciando servidor Django con nueva configuracion...
echo.
echo IMPORTANTE: Busca este mensaje al iniciar:
echo "MODO TESTING ACTIVADO: Autenticacion completamente deshabilitada"
echo.
echo Si no aparece, hay un problema con la configuracion.
echo.

cd backend
python manage.py runserver

pause

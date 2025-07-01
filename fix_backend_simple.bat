@echo off
echo =========================================
echo 🚀 Reparando AccountIA Backend 
echo =========================================

echo.
echo ⏳ Paso 1: Verificando servicios Docker...
docker-compose ps

echo.
echo ⏳ Paso 2: Iniciando servicios necesarios...
npm run docker:up

echo.
echo ⏳ Paso 3: Esperando que la base de datos esté lista...
timeout /t 5 /nobreak >nul

echo.
echo ⏳ Paso 4: Aplicando migraciones...
npm run backend:migrate

echo.
echo ⏳ Paso 5: Verificando que el backend responda...
echo Probando endpoint de salud...
curl -f http://localhost:8000/health/ || echo ❌ Backend no responde

echo.
echo ⏳ Paso 6: Creando usuario de prueba...
cd backend
python manage.py shell -c "
from django.contrib.auth import get_user_model
from declarations.models import Declaration

User = get_user_model()

# Crear usuario de prueba si no existe
test_user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={'first_name': 'Usuario', 'last_name': 'de Prueba'}
)

if created:
    print('✅ Usuario de prueba creado')
else:
    print('✅ Usuario de prueba ya existe')

# Verificar que podemos consultar declaraciones
try:
    count = Declaration.objects.count()
    active_count = Declaration.objects.filter(is_active=True).count()
    print(f'✅ Modelo verificado: {count} declaraciones total, {active_count} activas')
except Exception as e:
    print(f'❌ Error en modelo: {e}')

# Crear declaración de prueba
test_declaration, created = Declaration.objects.get_or_create(
    user=test_user,
    fiscal_year=2024,
    defaults={
        'title': 'Declaración Renta 2024',
        'status': 'draft',
        'total_income': 50000000,
        'total_withholdings': 3000000,
    }
)

if created:
    print('✅ Declaración de prueba creada')
else:
    print('✅ Declaración de prueba ya existe')
"

echo.
echo ⏳ Paso 7: Probando endpoint de declaraciones...
curl -X GET "http://localhost:8000/api/v1/declarations/" -H "Content-Type: application/json" || echo ❌ Endpoint de declaraciones falló

cd ..

echo.
echo =========================================
echo ✅ REPARACIÓN COMPLETADA
echo =========================================
echo.
echo 📝 Próximos pasos:
echo 1. Verificar que el frontend funcione: http://localhost:3000
echo 2. Si aún hay errores, revisar logs: npm run logs:backend
echo 3. Para reiniciar completamente: npm run docker:restart
echo.
pause

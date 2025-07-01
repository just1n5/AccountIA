# AccountIA Backend Fix Script
# Repara el problema de la columna is_active faltante

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Reparando AccountIA Backend" -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Cyan

function Test-ServiceHealth {
    param($Url, $ServiceName)
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $ServiceName está funcionando" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "❌ $ServiceName no responde" -ForegroundColor Red
        return $false
    }
}

# Paso 1: Verificar servicios Docker
Write-Host "`n⏳ Paso 1: Verificando servicios Docker..." -ForegroundColor Yellow
docker-compose ps

# Paso 2: Iniciar servicios
Write-Host "`n⏳ Paso 2: Iniciando servicios necesarios..." -ForegroundColor Yellow
npm run docker:up

# Paso 3: Esperar a que la base de datos esté lista
Write-Host "`n⏳ Paso 3: Esperando que la base de datos esté lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Paso 4: Aplicar migraciones
Write-Host "`n⏳ Paso 4: Aplicando migraciones..." -ForegroundColor Yellow
try {
    npm run backend:migrate
    Write-Host "✅ Migraciones aplicadas exitosamente" -ForegroundColor Green
} catch {
    Write-Host "❌ Error aplicando migraciones: $_" -ForegroundColor Red
    exit 1
}

# Paso 5: Verificar backend health
Write-Host "`n⏳ Paso 5: Verificando que el backend responda..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$backendHealthy = Test-ServiceHealth "http://localhost:8000/health/" "Backend API"

# Paso 6: Crear datos de prueba
Write-Host "`n⏳ Paso 6: Creando datos de prueba..." -ForegroundColor Yellow
$pythonScript = @"
from django.contrib.auth import get_user_model
from declarations.models import Declaration
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

try:
    # Crear usuario de prueba
    test_user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'first_name': 'Usuario', 'last_name': 'de Prueba'}
    )
    
    if created:
        print('✅ Usuario de prueba creado')
    else:
        print('✅ Usuario de prueba ya existe')
    
    # Verificar modelo Declaration
    count = Declaration.objects.count()
    active_count = Declaration.objects.filter(is_active=True).count()
    print(f'✅ Modelo verificado: {count} declaraciones total, {active_count} activas')
    
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
        
    print('✅ Todos los datos de prueba configurados correctamente')
    
except Exception as e:
    print(f'❌ Error configurando datos: {e}')
    exit(1)
"@

# Escribir script temporal
$tempScript = "temp_setup_data.py"
$pythonScript | Out-File -FilePath "backend\$tempScript" -Encoding UTF8

# Ejecutar script
try {
    Set-Location backend
    python $tempScript
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    Set-Location ..
    Write-Host "✅ Datos de prueba configurados" -ForegroundColor Green
} catch {
    Write-Host "❌ Error configurando datos de prueba: $_" -ForegroundColor Red
    Set-Location ..
}

# Paso 7: Probar endpoint de declaraciones
Write-Host "`n⏳ Paso 7: Probando endpoint de declaraciones..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$declarationsHealthy = Test-ServiceHealth "http://localhost:8000/api/v1/declarations/" "Endpoint de Declaraciones"

# Resumen final
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE REPARACIÓN" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($backendHealthy -and $declarationsHealthy) {
    Write-Host "✅ ÉXITO: Backend reparado completamente" -ForegroundColor Green
    Write-Host "`n📝 Próximos pasos:" -ForegroundColor Yellow
    Write-Host "1. Actualizar el frontend: Ctrl+F5 en el navegador" -ForegroundColor White
    Write-Host "2. Verificar dashboard: http://localhost:3000/dashboard" -ForegroundColor White
    Write-Host "3. Si hay problemas, verificar logs: npm run logs:backend" -ForegroundColor White
} else {
    Write-Host "❌ ADVERTENCIA: Algunos servicios pueden no estar funcionando" -ForegroundColor Yellow
    Write-Host "`n🔧 Soluciones:" -ForegroundColor Yellow
    Write-Host "1. Reiniciar servicios: npm run docker:restart" -ForegroundColor White
    Write-Host "2. Verificar logs: npm run logs" -ForegroundColor White
    Write-Host "3. Ejecutar este script nuevamente" -ForegroundColor White
}

Write-Host "`n🎯 Estado de servicios:" -ForegroundColor Cyan
Write-Host "- Backend Health: $(if($backendHealthy){'✅'}else{'❌'})" -ForegroundColor White
Write-Host "- Declarations API: $(if($declarationsHealthy){'✅'}else{'❌'})" -ForegroundColor White

Write-Host "`nPresiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

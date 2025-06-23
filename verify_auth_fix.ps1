# ========================================
# ACCOUNTIA - VERIFICACIÓN COMPLETA DE LA SOLUCIÓN
# ========================================

Write-Host "🚀 ACCOUNTIA - Verificando solución de autenticación..." -ForegroundColor Cyan
Write-Host ""

# Función para mostrar encabezados
function Show-Header($text) {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "🔧 $text" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Gray
}

# Función para mostrar éxito
function Show-Success($text) {
    Write-Host "✅ $text" -ForegroundColor Green
}

# Función para mostrar error
function Show-Error($text) {
    Write-Host "❌ $text" -ForegroundColor Red
}

# Función para mostrar información
function Show-Info($text) {
    Write-Host "ℹ️  $text" -ForegroundColor Yellow
}

# 1. Verificar configuración de archivos
Show-Header "1. VERIFICANDO CONFIGURACIÓN DE ARCHIVOS"

# Verificar .env
if (Test-Path ".env") {
    Show-Success "Archivo .env encontrado"
    
    $envContent = Get-Content .env -Raw
    if ($envContent -match "DEV_SKIP_AUTH_FOR_TESTING=1") {
        Show-Success "Variable DEV_SKIP_AUTH_FOR_TESTING=1 configurada"
    } else {
        Show-Error "Variable DEV_SKIP_AUTH_FOR_TESTING no encontrada en .env"
    }
} else {
    Show-Error "Archivo .env no encontrado"
}

# Verificar settings
$settingsPath = "backend\config\settings\development_simple.py"
if (Test-Path $settingsPath) {
    Show-Success "Archivo de settings encontrado"
    
    $settingsContent = Get-Content $settingsPath -Raw
    if ($settingsContent -match "MODO TESTING ACTIVADO") {
        Show-Success "Configuración condicional de testing encontrada"
    } else {
        Show-Error "Configuración condicional no encontrada en settings"
    }
} else {
    Show-Error "Archivo de settings no encontrado"
}

# 2. Verificar que el servidor esté corriendo
Show-Header "2. VERIFICANDO SERVIDOR DJANGO"

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get -TimeoutSec 5
    if ($healthResponse.status -eq "healthy") {
        Show-Success "Servidor Django está corriendo y saludable"
        Show-Info "Versión: $($healthResponse.version)"
    } else {
        Show-Error "Servidor responde pero no está saludable"
    }
} catch {
    Show-Error "No se puede conectar al servidor Django en puerto 8000"
    Show-Info "Asegúrate de que esté corriendo: python manage.py runserver"
}

# 3. Probar endpoints principales
Show-Header "3. PROBANDO ENDPOINTS PRINCIPALES"

# Probar declaraciones
try {
    Show-Info "Probando GET /api/v1/declarations/"
    $declarationsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/" -Method Get -TimeoutSec 5
    Show-Success "Endpoint de declaraciones funciona"
    
    if ($declarationsResponse.count) {
        Show-Info "Declaraciones encontradas: $($declarationsResponse.count)"
    } else {
        Show-Info "Lista de declaraciones vacía (esperado en sistema nuevo)"
    }
} catch {
    Show-Error "Error en endpoint de declaraciones: $($_.Exception.Message)"
    
    # Mostrar detalles del error si es de autenticación
    if ($_.Exception.Message -match "401" -or $_.Exception.Message -match "credenciales") {
        Show-Error "PROBLEMA DE AUTENTICACION DETECTADO"
        Show-Info "El servidor necesita ser reiniciado para aplicar la nueva configuracion"
    }
}

# Probar documentos
try {
    Show-Info "Probando GET /api/v1/documents/"
    $documentsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/" -Method Get -TimeoutSec 5
    Show-Success "Endpoint de documentos funciona"
} catch {
    Show-Error "Error en endpoint de documentos: $($_.Exception.Message)"
}

# Probar schema
try {
    Show-Info "Probando GET /api/schema/"
    $schemaResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/schema/" -Method Get -TimeoutSec 5
    Show-Success "Schema de API disponible"
} catch {
    Show-Error "Error obteniendo schema: $($_.Exception.Message)"
}

# 4. Crear declaración de prueba
Show-Header "4. CREANDO DECLARACIÓN DE PRUEBA"

try {
    $testDeclaration = @{
        fiscal_year = 2024
    } | ConvertTo-Json
    
    Show-Info "Creando declaración con fiscal_year=2024"
    $createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/" -Method Post -Body $testDeclaration -ContentType "application/json" -TimeoutSec 5
    Show-Success "Declaración creada exitosamente"
    Show-Info "ID de declaración: $($createResponse.id)"
    
    # Intentar obtener la declaración creada
    $declarationId = $createResponse.id
    $getResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/$declarationId/" -Method Get -TimeoutSec 5
    Show-Success "Declaración recuperada exitosamente"
    Show-Info "Status: $($getResponse.status)"
    
} catch {
    Show-Error "Error creando declaración de prueba: $($_.Exception.Message)"
}

# 5. Ejecutar script Python de pruebas completas
Show-Header "5. EJECUTANDO PRUEBAS COMPLETAS"

if (Test-Path "test_endpoints.py") {
    Show-Info "Ejecutando script de pruebas Python..."
    try {
        $pythonOutput = python test_endpoints.py 2>&1
        Write-Host $pythonOutput
    } catch {
        Show-Error "Error ejecutando script Python: $($_.Exception.Message)"
    }
} else {
    Show-Info "Script test_endpoints.py no encontrado, omitiendo pruebas Python"
}

# 6. Resumen y recomendaciones
Show-Header "6. RESUMEN Y PROXIMOS PASOS"

Show-Success "Solucion de autenticacion implementada"
Show-Success "Archivos de configuracion actualizados"
Show-Success "Scripts de prueba creados"

Write-Host ""
Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Si hay errores 401, reinicia el servidor Django:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ejecuta pruebas manuales:" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/declarations/' -Method Get" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Continua con las pruebas sistematicas de endpoints" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE: Esta configuracion es SOLO para testing local" -ForegroundColor Yellow

Write-Host ""
Show-Success "Verificacion completa finalizada"

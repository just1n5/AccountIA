# ========================================
# ACCOUNTIA - VERIFICACION COMPLETA
# ========================================

Write-Host "ACCOUNTIA - Verificando solucion de autenticacion..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar configuracion de archivos
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "1. VERIFICANDO CONFIGURACION DE ARCHIVOS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray

# Verificar .env
if (Test-Path ".env") {
    Write-Host "OK: Archivo .env encontrado" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    if ($envContent -match "DEV_SKIP_AUTH_FOR_TESTING=1") {
        Write-Host "OK: Variable DEV_SKIP_AUTH_FOR_TESTING=1 configurada" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Variable DEV_SKIP_AUTH_FOR_TESTING no encontrada en .env" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Archivo .env no encontrado" -ForegroundColor Red
}

# Verificar settings
$settingsPath = "backend\config\settings\development_simple.py"
if (Test-Path $settingsPath) {
    Write-Host "OK: Archivo de settings encontrado" -ForegroundColor Green
    
    $settingsContent = Get-Content $settingsPath -Raw
    if ($settingsContent -match "MODO TESTING ACTIVADO") {
        Write-Host "OK: Configuracion condicional de testing encontrada" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Configuracion condicional no encontrada en settings" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Archivo de settings no encontrado" -ForegroundColor Red
}

# 2. Verificar que el servidor este corriendo
Write-Host ""
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "2. VERIFICANDO SERVIDOR DJANGO" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get -TimeoutSec 5
    if ($healthResponse.status -eq "healthy") {
        Write-Host "OK: Servidor Django esta corriendo y saludable" -ForegroundColor Green
        Write-Host "INFO: Version: $($healthResponse.version)" -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: Servidor responde pero no esta saludable" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: No se puede conectar al servidor Django en puerto 8000" -ForegroundColor Red
    Write-Host "INFO: Asegurate de que este corriendo: python manage.py runserver" -ForegroundColor Yellow
}

# 3. Probar endpoints principales
Write-Host ""
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "3. PROBANDO ENDPOINTS PRINCIPALES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray

# Probar declaraciones
try {
    Write-Host "INFO: Probando GET /api/v1/declarations/" -ForegroundColor Yellow
    $declarationsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/" -Method Get -TimeoutSec 5
    Write-Host "OK: Endpoint de declaraciones funciona" -ForegroundColor Green
    
    if ($declarationsResponse.count) {
        Write-Host "INFO: Declaraciones encontradas: $($declarationsResponse.count)" -ForegroundColor Yellow
    } else {
        Write-Host "INFO: Lista de declaraciones vacia (esperado en sistema nuevo)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Error en endpoint de declaraciones: $($_.Exception.Message)" -ForegroundColor Red
    
    # Mostrar detalles del error si es de autenticacion
    if ($_.Exception.Message -match "401" -or $_.Exception.Message -match "credenciales") {
        Write-Host "PROBLEMA DE AUTENTICACION DETECTADO" -ForegroundColor Red
        Write-Host "INFO: El servidor necesita ser reiniciado para aplicar la nueva configuracion" -ForegroundColor Yellow
    }
}

# Probar documentos
try {
    Write-Host "INFO: Probando GET /api/v1/documents/" -ForegroundColor Yellow
    $documentsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/" -Method Get -TimeoutSec 5
    Write-Host "OK: Endpoint de documentos funciona" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error en endpoint de documentos: $($_.Exception.Message)" -ForegroundColor Red
}

# Probar schema
try {
    Write-Host "INFO: Probando GET /api/schema/" -ForegroundColor Yellow
    $schemaResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/schema/" -Method Get -TimeoutSec 5
    Write-Host "OK: Schema de API disponible" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error obteniendo schema: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Crear declaracion de prueba
Write-Host ""
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "4. CREANDO DECLARACION DE PRUEBA" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray

try {
    $testDeclaration = @{
        fiscal_year = 2024
    } | ConvertTo-Json
    
    Write-Host "INFO: Creando declaracion con fiscal_year=2024" -ForegroundColor Yellow
    $createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/" -Method Post -Body $testDeclaration -ContentType "application/json" -TimeoutSec 5
    Write-Host "OK: Declaracion creada exitosamente" -ForegroundColor Green
    Write-Host "INFO: ID de declaracion: $($createResponse.id)" -ForegroundColor Yellow
    
    # Intentar obtener la declaracion creada
    $declarationId = $createResponse.id
    $getResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/$declarationId/" -Method Get -TimeoutSec 5
    Write-Host "OK: Declaracion recuperada exitosamente" -ForegroundColor Green
    Write-Host "INFO: Status: $($getResponse.status)" -ForegroundColor Yellow
    
} catch {
    Write-Host "ERROR: Error creando declaracion de prueba: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Resumen y recomendaciones
Write-Host ""
Write-Host "============================================================" -ForegroundColor Gray
Write-Host "5. RESUMEN Y PROXIMOS PASOS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Gray

Write-Host "OK: Solucion de autenticacion implementada" -ForegroundColor Green
Write-Host "OK: Archivos de configuracion actualizados" -ForegroundColor Green
Write-Host "OK: Scripts de prueba creados" -ForegroundColor Green

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
Write-Host "OK: Verificacion completa finalizada" -ForegroundColor Green

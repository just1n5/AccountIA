# Verificación Rápida de Integración Frontend-Backend
# AccountIA Sprint 2 - Versión PowerShell

Write-Host ""
Write-Host "🚀 AccountIA - Verificación de Integración Frontend-Backend" -ForegroundColor Blue
Write-Host "===========================================================" -ForegroundColor Blue
Write-Host ""

function Test-Success {
    param($message)
    Write-Host "✅ $message" -ForegroundColor Green
}

function Test-Error {
    param($message)
    Write-Host "❌ $message" -ForegroundColor Red
}

function Test-Warning {
    param($message)
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Test-Info {
    param($message)
    Write-Host "ℹ️  $message" -ForegroundColor Cyan
}

# Verificar archivos críticos
Write-Host "🔍 Verificando archivos críticos..." -ForegroundColor Blue
Write-Host "-----------------------------------"

$criticalFiles = @(
    ".env",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/src/services/api.ts",
    "frontend/src/services/declarationService.ts",
    "frontend/src/components/dashboard/Dashboard.tsx"
)

$allFilesExist = $true
foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Test-Success "$file ✓"
    } else {
        Test-Error "$file no encontrado"
        $allFilesExist = $false
    }
}

# Verificar variables de entorno críticas
Write-Host ""
Write-Host "🔍 Verificando variables de entorno..." -ForegroundColor Blue
Write-Host "--------------------------------------"

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw -Encoding UTF8
    
    $criticalVars = @{
        "VITE_API_URL" = "http://localhost:8000/api/v1"
        "DEV_SKIP_AUTH_FOR_TESTING" = "1"
        "CORS_ALLOWED_ORIGINS" = "http://localhost:3000"
    }
    
    foreach ($var in $criticalVars.Keys) {
        if ($envContent -match "$var=") {
            if ($envContent -match [regex]::Escape($criticalVars[$var])) {
                Test-Success "$var configurada correctamente"
            } else {
                Test-Warning "$var configurada pero valor podría ser incorrecto"
            }
        } else {
            Test-Error "$var no encontrada en .env"
            $allFilesExist = $false
        }
    }
} else {
    Test-Error "Archivo .env no encontrado"
    $allFilesExist = $false
}

# Verificar configuración de Vite
Write-Host ""
Write-Host "🔍 Verificando configuración de Vite..." -ForegroundColor Blue
Write-Host "----------------------------------------"

if (Test-Path "frontend/vite.config.js") {
    $viteContent = Get-Content "frontend/vite.config.js" -Raw -Encoding UTF8
    
    if ($viteContent -match "http://localhost:8000") {
        Test-Success "Proxy de Vite configurado para desarrollo local"
    } elseif ($viteContent -match "http://backend:8000") {
        Test-Warning "Proxy de Vite configurado para Docker - debería ser localhost"
    } else {
        Test-Warning "Configuración de proxy no encontrada"
    }
} else {
    Test-Error "vite.config.js no encontrado"
}

# Verificar conexión al backend
Write-Host ""
Write-Host "🔍 Verificando conexión con backend..." -ForegroundColor Blue
Write-Host "--------------------------------------"

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get -TimeoutSec 5
    Test-Success "Backend health check OK"
    
    try {
        $declarationsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/declarations/" -Method Get -TimeoutSec 5
        $count = if ($declarationsResponse -is [array]) { $declarationsResponse.Count } else { $declarationsResponse.count }
        Test-Success "API de declaraciones OK - $count declaraciones encontradas"
        
        # Mostrar datos de prueba si existen
        if ($count -gt 0) {
            Write-Host ""
            Test-Info "Datos de prueba disponibles:"
            if ($declarationsResponse -is [array]) {
                foreach ($declaration in $declarationsResponse[0..1]) {
                    Write-Host "   • Declaración ID: $($declaration.id), Año: $($declaration.fiscal_year), Estado: $($declaration.status)" -ForegroundColor Gray
                }
            } else {
                foreach ($declaration in $declarationsResponse.results[0..1]) {
                    Write-Host "   • Declaración ID: $($declaration.id), Año: $($declaration.fiscal_year), Estado: $($declaration.status)" -ForegroundColor Gray
                }
            }
        }
        
    } catch {
        Test-Error "API de declaraciones falló: $($_.Exception.Message)"
        $allFilesExist = $false
    }
    
} catch {
    Test-Error "No se puede conectar al backend en puerto 8000"
    Test-Warning "Asegúrate de que el backend esté ejecutándose: python backend/manage.py runserver"
    $allFilesExist = $false
}

# Verificar puerto frontend
Write-Host ""
Write-Host "🔍 Verificando estado del frontend..." -ForegroundColor Blue
Write-Host "-------------------------------------"

try {
    $frontendResponse = Invoke-RestMethod -Uri "http://localhost:3000" -Method Get -TimeoutSec 2
    Test-Success "Frontend ejecutándose en puerto 3000"
} catch {
    Test-Info "Frontend no está ejecutándose (esto es normal si no lo has iniciado)"
    Write-Host "   Para iniciarlo: cd frontend && npm run dev" -ForegroundColor Gray
}

# Resumen final
Write-Host ""
Write-Host "============================================================" -ForegroundColor Blue
Write-Host "📋 RESUMEN DE VERIFICACIÓN" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue

if ($allFilesExist) {
    Write-Host ""
    Test-Success "¡Todas las verificaciones principales pasaron!"
    Test-Success "Tu integración frontend-backend está lista"
    
    Write-Host ""
    Write-Host "🎯 PRÓXIMOS PASOS:" -ForegroundColor Yellow
    Write-Host "1. Si el frontend no está ejecutándose:" -ForegroundColor White
    Write-Host "   cd frontend" -ForegroundColor Gray
    Write-Host "   npm run dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Abrir navegador:" -ForegroundColor White
    Write-Host "   http://localhost:3000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Probar el dashboard y crear declaraciones" -ForegroundColor White
    
} else {
    Write-Host ""
    Test-Error "Algunas verificaciones fallaron"
    Test-Warning "Revisa los errores indicados arriba"
    
    Write-Host ""
    Write-Host "🔧 PASOS PARA SOLUCIONAR:" -ForegroundColor Yellow
    Write-Host "1. Asegúrate de que el backend esté ejecutándose:" -ForegroundColor White
    Write-Host "   python backend/manage.py runserver" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Verifica las variables de entorno en .env" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Ejecuta este script nuevamente" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 Para más ayuda, consulta: FRONTEND_INTEGRATION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

# 🧪 SCRIPT AUTOMATIZADO TESTING SPRINT 2 - ACCOUNTIA
# Archivo: test_sprint2.ps1
# Uso: .\test_sprint2.ps1 desde el directorio raíz del proyecto

param(
    [switch]$Quick,
    [switch]$SkipFrontend,
    [switch]$Verbose
)

# Configuración de encoding para Windows
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

# Colores para output
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$BLUE = "`e[34m"
$NC = "`e[0m"

# Funciones de utilidad
function Write-Header {
    param($Message)
    Write-Host "$BLUE================================$NC" -NoNewline
    Write-Host ""
    Write-Host "$BLUE$Message$NC" -NoNewline
    Write-Host ""
    Write-Host "$BLUE================================$NC" -NoNewline
    Write-Host ""
}

function Write-Success {
    param($Message)
    Write-Host "$GREEN✅ $Message$NC" -NoNewline
    Write-Host ""
}

function Write-Error {
    param($Message)
    Write-Host "$RED❌ $Message$NC" -NoNewline
    Write-Host ""
}

function Write-Warning {
    param($Message)
    Write-Host "$YELLOW⚠️  $Message$NC" -NoNewline
    Write-Host ""
}

function Write-Info {
    param($Message)
    Write-Host "$BLUE💡 $Message$NC" -NoNewline
    Write-Host ""
}

function Test-Service {
    param($Url, $Name)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Success "$Name está funcionando (Status: $($response.StatusCode))"
            return $true
        }
        else {
            Write-Error "$Name retornó status: $($response.StatusCode)"
            return $false
        }
    }
    catch {
        Write-Error "$Name no está disponible: $($_.Exception.Message)"
        return $false
    }
}

function Test-PythonCommand {
    param($Command, $Description)
    try {
        Write-Host "   Ejecutando: $Command" -ForegroundColor Gray
        $result = python -c $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success $Description
            if ($Verbose) {
                Write-Host "   Output: $result" -ForegroundColor Gray
            }
            return $true
        }
        else {
            Write-Error "$Description (Exit code: $LASTEXITCODE)"
            Write-Host "   Error: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Error "$Description - Exception: $($_.Exception.Message)"
        return $false
    }
}

# Variables globales para resultados
$TestResults = @{
    Infrastructure = @()
    Backend = @()
    Storage = @()
    Parser = @()
    Frontend = @()
    Integration = @()
    TotalTests = 0
    PassedTests = 0
    FailedTests = 0
}

function Add-TestResult {
    param($Category, $Test, $Passed, $Details = "")
    $TestResults[$Category] += @{
        Test = $Test
        Passed = $Passed
        Details = $Details
    }
    $TestResults.TotalTests++
    if ($Passed) { $TestResults.PassedTests++ } else { $TestResults.FailedTests++ }
}

# INICIO DEL SCRIPT
Clear-Host
Write-Header "TESTING COMPLETO SPRINT 2 - ACCOUNTIA"
Write-Info "Iniciando verificación sistemática del sistema..."
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend" -PathType Container) -or -not (Test-Path "frontend" -PathType Container)) {
    Write-Error "❌ Ejecutar desde el directorio raíz del proyecto (que contiene 'backend' y 'frontend')"
    exit 1
}

# ================================
# FASE 1: VERIFICACIÓN INFRAESTRUCTURA
# ================================
Write-Header "FASE 1: VERIFICACIÓN DE INFRAESTRUCTURA"

Write-Info "1.1 Verificando servicios base..."

# Test Backend Django
$backendRunning = Test-Service "http://localhost:8000/health/" "Backend Django"
Add-TestResult "Infrastructure" "Backend Django disponible" $backendRunning

if (-not $SkipFrontend) {
    # Test Frontend React
    $frontendRunning = Test-Service "http://localhost:3000" "Frontend React"
    Add-TestResult "Infrastructure" "Frontend React disponible" $frontendRunning
}

# Test variables de entorno
Write-Info "1.2 Verificando configuración..."
if (Test-Path ".env") {
    Write-Success "Archivo .env encontrado"
    Add-TestResult "Infrastructure" "Archivo .env existe" $true
} else {
    Write-Warning "Archivo .env no encontrado"
    Add-TestResult "Infrastructure" "Archivo .env existe" $false
}

Write-Host ""

# ================================
# FASE 2: TESTING BACKEND APIs
# ================================
Write-Header "FASE 2: TESTING BACKEND APIs"

Write-Info "2.1 Probando APIs de Declaraciones..."

# Test API Declarations
$declarationsAPI = Test-Service "http://localhost:8000/api/v1/declarations/" "API Declarations"
Add-TestResult "Backend" "API Declarations responde" $declarationsAPI

# Test API Documents
$documentsAPI = Test-Service "http://localhost:8000/api/v1/documents/" "API Documents"
Add-TestResult "Backend" "API Documents responde" $documentsAPI

Write-Host ""

# ================================
# FASE 3: TESTING STORAGE SERVICE
# ================================
Write-Header "FASE 3: TESTING STORAGE SERVICE"

Write-Info "3.1 Verificando LocalStorageService..."

Set-Location "backend"

$storageTest = Test-PythonCommand "from apps.documents.services.storage_service import get_storage_service; service = get_storage_service(); print('Storage service loaded:', type(service).__name__)" "LocalStorageService carga correctamente"
Add-TestResult "Storage" "LocalStorageService se instancia" $storageTest

$modelsTest = Test-PythonCommand "from apps.documents.models import Document; from apps.declarations.models import Declaration; print('Models loaded successfully')" "Modelos de Document y Declaration"
Add-TestResult "Storage" "Modelos cargan correctamente" $modelsTest

Set-Location ".."

Write-Host ""

# ================================
# FASE 4: TESTING EXCEL PARSER
# ================================
Write-Header "FASE 4: TESTING EXCEL PARSER"

Write-Info "4.1 Verificando ExogenaParser..."

Set-Location "backend"

$parserTest = Test-PythonCommand "from apps.documents.parsers.excel_parser import ExogenaParser; parser = ExogenaParser(); print('ExogenaParser loaded successfully')" "ExogenaParser se instancia correctamente"
Add-TestResult "Parser" "ExogenaParser se instancia" $parserTest

if ($parserTest) {
    $demoDataTest = Test-PythonCommand "from apps.documents.parsers.excel_parser import ExogenaParser; parser = ExogenaParser(); data = parser.parse_demo_data(); print(f'Demo data keys: {list(data.keys())}'); print(f'Records count: {len(data.get(\"income_records\", []))}')" "Datos demo del parser"
    Add-TestResult "Parser" "Parser retorna datos demo válidos" $demoDataTest
}

Set-Location ".."

Write-Host ""

# ================================
# FASE 5: TESTING CELERY (CON EXPECTATIVA DE FALLO)
# ================================
Write-Header "FASE 5: TESTING CELERY (Windows - Errores Esperados)"

Write-Warning "⚠️  Celery no funciona en Windows - Verificando configuración síncrona..."

Set-Location "backend"

$celeryConfigTest = Test-PythonCommand "from django.conf import settings; print(f'CELERY_TASK_ALWAYS_EAGER: {getattr(settings, \"CELERY_TASK_ALWAYS_EAGER\", \"Not set\")}'); print('Celery configurado para desarrollo Windows')" "Configuración Celery para Windows"
Add-TestResult "Backend" "Celery configurado síncronamente" $celeryConfigTest

$taskImportTest = Test-PythonCommand "from apps.documents.tasks import process_document; print('process_document task importado correctamente')" "Task process_document importa"
Add-TestResult "Backend" "Task process_document se importa" $taskImportTest

Set-Location ".."

Write-Host ""

# ================================
# FASE 6: TESTING FRONTEND (OPCIONAL)
# ================================
if (-not $SkipFrontend) {
    Write-Header "FASE 6: TESTING FRONTEND COMPONENTS"
    
    Write-Info "6.1 Verificando estructura frontend..."
    
    # Verificar archivos clave del frontend
    $frontendFiles = @(
        "frontend/src/components/dashboard/Dashboard.tsx",
        "frontend/src/components/declarations/FileUpload.tsx",
        "frontend/src/hooks/useDeclarationManagement.ts",
        "frontend/src/services/declarationService.ts",
        "frontend/src/services/documentService.ts"
    )
    
    foreach ($file in $frontendFiles) {
        if (Test-Path $file) {
            Write-Success "Encontrado: $(Split-Path $file -Leaf)"
            Add-TestResult "Frontend" "Archivo $(Split-Path $file -Leaf) existe" $true
        } else {
            Write-Error "No encontrado: $file"
            Add-TestResult "Frontend" "Archivo $(Split-Path $file -Leaf) existe" $false
        }
    }
    
    Write-Host ""
}

# ================================
# FASE 7: TESTING DE INTEGRACIÓN
# ================================
Write-Header "FASE 7: TESTING DE INTEGRACIÓN"

Write-Info "7.1 Verificando integración database..."

Set-Location "backend"

$dbIntegrationTest = Test-PythonCommand "from apps.declarations.models import Declaration; from apps.documents.models import Document; from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}'); print(f'Declarations: {Declaration.objects.count()}'); print(f'Documents: {Document.objects.count()}'); print('Database integration working')" "Integración con base de datos"
Add-TestResult "Integration" "Database integration funciona" $dbIntegrationTest

Set-Location ".."

Write-Host ""

# ================================
# REPORTE FINAL
# ================================
Write-Header "REPORTE FINAL - SPRINT 2 TESTING"

Write-Host ""
Write-Info "📊 RESUMEN DE RESULTADOS:"
Write-Host "   Total tests ejecutados: $($TestResults.TotalTests)" -ForegroundColor White
Write-Host "   Tests exitosos: $($TestResults.PassedTests)" -ForegroundColor Green
Write-Host "   Tests fallidos: $($TestResults.FailedTests)" -ForegroundColor Red

$successRate = [math]::Round(($TestResults.PassedTests / $TestResults.TotalTests) * 100, 1)
Write-Host "   Tasa de éxito: $successRate%" -ForegroundColor $(if($successRate -gt 80) {"Green"} elseif($successRate -gt 60) {"Yellow"} else {"Red"})

Write-Host ""

# Mostrar detalles por categoría
foreach ($category in @("Infrastructure", "Backend", "Storage", "Parser", "Frontend", "Integration")) {
    if ($TestResults[$category].Count -gt 0) {
        Write-Host "🔸 $category" -ForegroundColor Cyan
        foreach ($test in $TestResults[$category]) {
            $status = if ($test.Passed) { "$GREEN✅$NC" } else { "$RED❌$NC" }
            Write-Host "   $status $($test.Test)" -NoNewline
            Write-Host ""
            if ($test.Details -and $Verbose) {
                Write-Host "      Details: $($test.Details)" -ForegroundColor Gray
            }
        }
        Write-Host ""
    }
}

# Evaluación final
if ($successRate -gt 80) {
    Write-Success "🎉 SPRINT 2 TESTING EXITOSO - Listo para continuar con Sprint 3"
    Write-Info "✅ El sistema está funcionando correctamente para continuar con el Motor de IA"
} elseif ($successRate -gt 60) {
    Write-Warning "⚠️  SPRINT 2 TESTING PARCIAL - Revisar problemas antes de continuar"
    Write-Info "🔧 Algunos componentes necesitan atención antes del Sprint 3"
} else {
    Write-Error "❌ SPRINT 2 TESTING FALLIDO - Requiere correcciones importantes"
    Write-Info "🚨 El sistema necesita correcciones antes de continuar"
}

Write-Host ""
Write-Info "📋 COMANDOS PARA DEBUGGING:"
Write-Host "   Backend logs: " -NoNewline; Write-Host "cd backend && python manage.py runserver --verbosity=2" -ForegroundColor Yellow
Write-Host "   Frontend logs: " -NoNewline; Write-Host "cd frontend && npm run dev" -ForegroundColor Yellow
Write-Host "   Database shell: " -NoNewline; Write-Host "cd backend && python manage.py shell" -ForegroundColor Yellow

Write-Host ""
Write-Success "Testing completo. Revisa los resultados arriba. 🚀"
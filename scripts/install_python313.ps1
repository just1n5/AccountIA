# 🔧 Installer para Python 3.13 - Windows
# Versión específica para Python 3.13 desde Microsoft Store

Write-Host "🚀 Instalando dependencias Python 3.13 para Windows..." -ForegroundColor Blue
Write-Host ""

# Verificar ubicación
if (-not (Test-Path "requirements.txt") -and -not (Test-Path "requirements_python313.txt")) {
    Write-Host "❌ Error: Debes ejecutar este script desde el directorio backend" -ForegroundColor Red
    Write-Host "   Ubicación actual: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Uso correcto: cd backend && powershell -File ../scripts/install_python313.ps1" -ForegroundColor Yellow
    exit 1
}

# Verificar Python 3.13
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
    
    # Verificar si es Python 3.13
    if ($pythonVersion -match "3\.13") {
        Write-Host "ℹ️  Detectado Python 3.13 - usando configuración especial" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  No es Python 3.13 - usando configuración estándar" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "   Instala Python desde: https://python.org" -ForegroundColor Yellow
    exit 1
}

# CRÍTICO: Instalar setuptools y wheel primero para Python 3.13
Write-Host "🛠️  Instalando herramientas de build críticas..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Herramientas de build instaladas" -ForegroundColor Green
} else {
    Write-Host "❌ Error instalando herramientas de build" -ForegroundColor Red
    exit 1
}

# Verificar setuptools
try {
    $result = python -c "import setuptools; print(f'setuptools: {setuptools.__version__}')" 2>&1
    Write-Host "✅ $result" -ForegroundColor Green
} catch {
    Write-Host "❌ setuptools no disponible" -ForegroundColor Red
    exit 1
}

# Instalar dependencias específicas para Python 3.13
Write-Host "📦 Instalando dependencias compatibles con Python 3.13..." -ForegroundColor Cyan

# Usar requirements específico para Python 3.13 si existe
$requirementsFile = ""
if (Test-Path "requirements_python313.txt") {
    $requirementsFile = "requirements_python313.txt"
    Write-Host "   Usando requirements_python313.txt" -ForegroundColor Gray
} elseif (Test-Path "requirements_windows.txt") {
    $requirementsFile = "requirements_windows.txt"
    Write-Host "   Usando requirements_windows.txt" -ForegroundColor Gray
} elseif (Test-Path "requirements.txt") {
    $requirementsFile = "requirements.txt"
    Write-Host "   Usando requirements.txt" -ForegroundColor Gray
} else {
    Write-Host "❌ No se encontró archivo requirements" -ForegroundColor Red
    exit 1
}

# Instalar dependencias
Write-Host "📋 Instalando desde $requirementsFile..." -ForegroundColor Cyan
python -m pip install -r $requirementsFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas exitosamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Algunas dependencias fallaron, intentando instalación individual..." -ForegroundColor Yellow
    
    # Instalar paquetes críticos uno por uno
    $criticalPackages = @(
        "Django==4.2.16",
        "djangorestframework==3.15.2",
        "django-cors-headers==4.3.1",
        "psycopg2-binary==2.9.9",
        "requests==2.31.0"
    )
    
    foreach ($package in $criticalPackages) {
        Write-Host "   Instalando $package..." -ForegroundColor Gray
        python -m pip install $package
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $package" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Error con $package" -ForegroundColor Yellow
        }
    }
}

# Verificar instalaciones críticas
Write-Host "🔍 Verificando instalaciones críticas..." -ForegroundColor Cyan

$tests = @(
    @{ Name = "Django"; Command = "import django; print('Django:', django.__version__)" },
    @{ Name = "DRF"; Command = "import rest_framework; print('DRF:', rest_framework.__version__)" },
    @{ Name = "psycopg2"; Command = "import psycopg2; print('psycopg2: OK')" },
    @{ Name = "requests"; Command = "import requests; print('requests:', requests.__version__)" }
)

$successCount = 0
foreach ($test in $tests) {
    try {
        $result = python -c $test.Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($test.Name): $result" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "   ❌ $($test.Name): Error" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "   ❌ $($test.Name): No instalado" -ForegroundColor Red
    }
}

# Verificar Django específicamente
Write-Host "🔍 Verificando Django..." -ForegroundColor Cyan
try {
    python -c "import django; print('Django versión:', django.get_version())"
    Write-Host "✅ Django funcional" -ForegroundColor Green
}
catch {
    Write-Host "❌ Django no funcional" -ForegroundColor Red
}

# Mostrar resumen
Write-Host ""
Write-Host "📊 Resumen:" -ForegroundColor Blue
Write-Host "   Paquetes críticos funcionando: $successCount/4" -ForegroundColor White

if ($successCount -ge 3) {
    Write-Host "🎉 Instalación completada con éxito!" -ForegroundColor Green
    Write-Host "   Próximos pasos:" -ForegroundColor Cyan
    Write-Host "   1. cd .." -ForegroundColor Gray
    Write-Host "   2. npm run docker:up" -ForegroundColor Gray
    Write-Host "   3. npm run backend:dev" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Instalación parcial - algunos paquetes fallaron" -ForegroundColor Yellow
    Write-Host "   Considera usar Python 3.11 para mayor compatibilidad" -ForegroundColor Cyan
}

Write-Host ""
exit 0

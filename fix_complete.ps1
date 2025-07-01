# AccountIA - Reparación Completa
# Soluciona URLs duplicadas e inicia backend

Write-Host "🚀 REPARACIÓN COMPLETA ACCOUNTIA" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Función para verificar si un puerto está en uso
function Test-Port {
    param($Port)
    try {
        $connection = New-Object Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

Write-Host "`n[1/4] 🔧 Verificando estado actual..." -ForegroundColor Yellow

# Verificar si backend ya está corriendo
if (Test-Port 8000) {
    Write-Host "⚠️  Backend ya está corriendo en puerto 8000" -ForegroundColor Yellow
    $restart = Read-Host "¿Quieres reiniciarlo? (y/N)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        Write-Host "🔄 Necesitarás detener el proceso manualmente y ejecutar este script de nuevo" -ForegroundColor Yellow
        exit
    }
} else {
    Write-Host "✅ Puerto 8000 disponible" -ForegroundColor Green
}

Write-Host "`n[2/4] 🔧 Corrigiendo configuración del frontend..." -ForegroundColor Yellow

# Crear backup del archivo original
$apiFile = "frontend\src\services\api.ts"
$apiFixedFile = "frontend\src\services\api_fixed.ts"
$apiBackupFile = "frontend\src\services\api_backup.ts"

if (Test-Path $apiFile) {
    Copy-Item $apiFile $apiBackupFile -Force
    Write-Host "✅ Backup creado: api_backup.ts" -ForegroundColor Green
}

# Aplicar el fix
if (Test-Path $apiFixedFile) {
    Copy-Item $apiFixedFile $apiFile -Force
    Write-Host "✅ Configuración API corregida (URLs duplicadas resueltas)" -ForegroundColor Green
} else {
    Write-Host "❌ Archivo de fix no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/4] 🗄️ Configurando base de datos..." -ForegroundColor Yellow

try {
    Set-Location backend
    
    # Verificar Python
    $pythonVersion = python --version 2>&1
    Write-Host "🐍 $pythonVersion" -ForegroundColor Green
    
    # Aplicar migraciones
    Write-Host "🔧 Aplicando migraciones..." -ForegroundColor Yellow
    python manage.py migrate --verbosity=2
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migraciones aplicadas exitosamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error aplicando migraciones" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    
} catch {
    Write-Host "❌ Error configurando base de datos: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "`n[4/4] 🚀 Iniciando servidor backend..." -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan

Write-Host "`n📊 ESTADO DEL SISTEMA:" -ForegroundColor Cyan
Write-Host "✅ URLs del frontend corregidas" -ForegroundColor Green
Write-Host "✅ Migraciones aplicadas" -ForegroundColor Green
Write-Host "✅ Base de datos configurada" -ForegroundColor Green

Write-Host "`n📍 URLS DEL SISTEMA:" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Health:   http://localhost:8000/health/" -ForegroundColor White
Write-Host "API:      http://localhost:8000/api/v1/" -ForegroundColor White

Write-Host "`n💡 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. ✅ Backend se iniciará automáticamente" -ForegroundColor Green
Write-Host "2. 🔄 Abrir nueva terminal para frontend:" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host "3. 🌐 Ir a http://localhost:3000/dashboard" -ForegroundColor Yellow

Write-Host "`n⏹️  Para detener el backend: Ctrl+C" -ForegroundColor Red
Write-Host "`n🚀 INICIANDO BACKEND..." -ForegroundColor Green
Write-Host "-" * 50 -ForegroundColor Gray

try {
    python manage.py runserver 8000
} catch {
    Write-Host "`n❌ Error iniciando servidor: $_" -ForegroundColor Red
} finally {
    Set-Location ..
    Write-Host "`n✅ Backend terminado" -ForegroundColor Green
}

Write-Host "`nPresiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

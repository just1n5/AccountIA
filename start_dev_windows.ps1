# AccountIA - Script de Desarrollo para Windows PowerShell
# Configura encoding UTF-8 y ejecuta servicios

Write-Host "================================" -ForegroundColor Blue
Write-Host "AccountIA - Modo Desarrollo" -ForegroundColor Blue  
Write-Host "================================" -ForegroundColor Blue
Write-Host ""

# Configurar variables de entorno para UTF-8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "1"
$env:PYTHONUTF8 = "1"
$env:PYTHONLEGACYWINDOWSFS = "1"

Write-Host "[INFO] Configurado encoding UTF-8 para Python" -ForegroundColor Green
Write-Host "[INFO] Variables configuradas:" -ForegroundColor Cyan
Write-Host "  - PYTHONIOENCODING: $env:PYTHONIOENCODING" -ForegroundColor Gray
Write-Host "  - PYTHONUTF8: $env:PYTHONUTF8" -ForegroundColor Gray
Write-Host ""

Write-Host "[INIT] Iniciando servicios de desarrollo..." -ForegroundColor Yellow
Write-Host "[INIT] Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "[INIT] Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host ""

# Ejecutar desarrollo
try {
    npm run dev
} catch {
    Write-Host "[ERROR] Error ejecutando npm run dev: $_" -ForegroundColor Red
    Write-Host "[INFO] Presiona cualquier tecla para continuar..." -ForegroundColor Yellow
    $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host ""
Write-Host "[DONE] Servicios terminados" -ForegroundColor Green

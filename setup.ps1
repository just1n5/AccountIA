# ================================
# AccountIA - Windows Setup Script
# ================================

Write-Host "=================================================="
Write-Host "🚀 AccountIA - Setup Script for Windows"
Write-Host "=================================================="
Write-Host ""

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Cyan"

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

# Check if Docker is installed
Write-Info "Checking Docker installation..."
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Success "Docker is installed"
} else {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
    Write-Host "Download from: https://www.docker.com/products/docker-desktop/"
    exit 1
}

# Check if Docker Compose is available
Write-Info "Checking Docker Compose..."
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Success "Docker Compose is available"
} else {
    Write-Error "Docker Compose is not available"
    exit 1
}

# Create .env file if it doesn't exist
Write-Info "Setting up environment variables..."
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Success "Created .env file from template"
    Write-Warning "Please edit .env file with your actual configuration values"
} else {
    Write-Warning ".env file already exists, skipping..."
}

# Build and start containers
Write-Info "Building Docker images (this may take a few minutes)..."
try {
    docker-compose build
    Write-Success "Docker images built successfully"
} catch {
    Write-Error "Failed to build Docker images"
    exit 1
}

Write-Info "Starting services..."
try {
    docker-compose up -d postgres redis
    Write-Success "Database services started"
    
    # Wait for database to be ready
    Write-Info "Waiting for database to be ready..."
    Start-Sleep -Seconds 10
    
    # Start all services
    docker-compose up -d
    Write-Success "All services started"
} catch {
    Write-Error "Failed to start services"
    exit 1
}

# Display success message
Write-Host ""
Write-Host "=================================================="
Write-Success "AccountIA setup completed successfully! 🎉"
Write-Host "=================================================="
Write-Host ""

Write-Info "Available services:"
Write-Host "• Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "• Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "• Admin:     http://localhost:8000/admin" -ForegroundColor White
Write-Host "• PgAdmin:   http://localhost:5050" -ForegroundColor White
Write-Host "• MailHog:   http://localhost:8025" -ForegroundColor White
Write-Host ""

Write-Info "Next steps:"
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "3. Check logs: docker-compose logs -f" -ForegroundColor White
Write-Host ""

Write-Warning "Don't forget to:"
Write-Host "• Configure Firebase authentication" -ForegroundColor White
Write-Host "• Set up Google Cloud Platform project" -ForegroundColor White
Write-Host "• Update database credentials" -ForegroundColor White
Write-Host "• Configure AI service API keys" -ForegroundColor White
#!/bin/bash

# ================================
# AccountIA - Setup Script
# ================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🚀 AccountIA - Setup Script"
    echo "=================================================="
    echo -e "${NC}"
}

# Check if required tools are installed
check_requirements() {
    print_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Make
    if ! command -v make &> /dev/null; then
        print_warning "Make is not installed. You'll need to run commands manually."
    fi
    
    print_success "All requirements are met!"
}

# Create environment file
setup_environment() {
    print_info "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your actual configuration values"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    directories=(
        "backend/apps/authentication/migrations"
        "backend/apps/users/migrations"
        "backend/apps/declarations/migrations"
        "backend/apps/documents/migrations"
        "backend/apps/ai_core/migrations"
        "backend/apps/payments/migrations"
        "backend/core"
        "backend/static"
        "backend/media/uploads"
        "backend/templates/emails"
        "backend/fixtures"
        "backend/scripts"
        "frontend/src/components/ui"
        "frontend/src/components/layout"
        "frontend/src/components/auth"
        "frontend/src/components/declaration"
        "frontend/src/pages/DeclarationFlow"
        "frontend/src/hooks"
        "frontend/src/services"
        "frontend/src/store"
        "frontend/src/utils"
        "frontend/src/types"
        "frontend/src/styles"
        "frontend/tests"
        "ai_knowledge/documents/estatuto_tributario"
        "ai_knowledge/documents/dian_concepts"
        "ai_knowledge/documents/regulations"
        "ai_knowledge/processed"
        "ai_knowledge/scripts"
        "ai_knowledge/config"
        "database/scripts"
        "database/fixtures"
        "database/schemas"
        "infrastructure/docker/backend"
        "infrastructure/docker/frontend"
        "infrastructure/docker/nginx"
        "infrastructure/gcp/terraform"
        "infrastructure/gcp/cloudbuild"
        "infrastructure/gcp/scripts"
        "infrastructure/monitoring/prometheus"
        "infrastructure/monitoring/grafana"
        "tests/integration"
        "tests/e2e"
        "tests/load"
        "tests/fixtures"
        "scripts"
        "tools/code-quality"
        "tools/monitoring"
        "tools/utilities"
        "logs"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    print_success "Created all necessary directories"
}

# Create basic Python files for Django apps
create_python_files() {
    print_info "Creating basic Python files..."
    
    # Django apps
    apps=("authentication" "users" "declarations" "documents" "ai_core" "payments" "common")
    
    for app in "${apps[@]}"; do
        app_dir="backend/apps/$app"
        
        # Create __init__.py files
        touch "$app_dir/__init__.py"
        touch "$app_dir/migrations/__init__.py"
        
        # Create basic app files if they don't exist
        [ ! -f "$app_dir/models.py" ] && echo "# $app models" > "$app_dir/models.py"
        [ ! -f "$app_dir/views.py" ] && echo "# $app views" > "$app_dir/views.py"
        [ ! -f "$app_dir/urls.py" ] && echo "# $app URLs" > "$app_dir/urls.py"
        [ ! -f "$app_dir/apps.py" ] && echo "# $app app config" > "$app_dir/apps.py"
        [ ! -f "$app_dir/serializers.py" ] && echo "# $app serializers" > "$app_dir/serializers.py"
        [ ! -f "$app_dir/admin.py" ] && echo "# $app admin" > "$app_dir/admin.py"
        
        # Create tests directory
        mkdir -p "$app_dir/tests"
        touch "$app_dir/tests/__init__.py"
        [ ! -f "$app_dir/tests/test_models.py" ] && echo "# $app model tests" > "$app_dir/tests/test_models.py"
        [ ! -f "$app_dir/tests/test_views.py" ] && echo "# $app view tests" > "$app_dir/tests/test_views.py"
    done
    
    # Core files
    touch "backend/core/__init__.py"
    
    print_success "Created basic Python files"
}

# Create git repository
setup_git() {
    print_info "Setting up Git repository..."
    
    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "🎉 Initial commit: AccountIA project setup"
        print_success "Git repository initialized"
    else
        print_warning "Git repository already exists, skipping..."
    fi
}

# Display final instructions
show_instructions() {
    print_header
    print_success "AccountIA setup completed successfully! 🎉"
    echo ""
    print_info "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Start the development environment:"
    echo "   make dev"
    echo "3. Or run manually:"
    echo "   docker-compose up -d"
    echo ""
    print_info "Available services after startup:"
    echo "• Frontend:  http://localhost:3000"
    echo "• Backend:   http://localhost:8000"
    echo "• Admin:     http://localhost:8000/admin"
    echo "• PgAdmin:   http://localhost:5050"
    echo "• MailHog:   http://localhost:8025"
    echo ""
    print_info "Useful commands:"
    echo "• make help        - Show all available commands"
    echo "• make logs        - View logs from all services"
    echo "• make shell-backend - Open Django shell"
    echo "• make test        - Run all tests"
    echo ""
    print_warning "Don't forget to:"
    echo "• Configure Firebase authentication"
    echo "• Set up Google Cloud Platform project"
    echo "• Update database credentials"
    echo "• Configure AI service API keys"
}

# Main execution
main() {
    print_header
    
    check_requirements
    setup_environment
    create_directories
    create_python_files
    setup_git
    
    show_instructions
}

# Run the main function
main "$@"
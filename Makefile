# ================================
# AccountIA - Makefile
# ================================

.PHONY: help
.DEFAULT_GOAL := help

# Colors for terminal output
RESET=\033[0m
BOLD=\033[1m
RED=\033[31m
GREEN=\033[32m
YELLOW=\033[33m
BLUE=\033[34m
MAGENTA=\033[35m
CYAN=\033[36m

# Project variables
PROJECT_NAME=accountia
DOCKER_COMPOSE=docker-compose
DOCKER_COMPOSE_FILE=docker-compose.yml
BACKEND_CONTAINER=accountia_backend
FRONTEND_CONTAINER=accountia_frontend
DB_CONTAINER=accountia_postgres

help: ## 📖 Show this help message
	@echo "$(BOLD)$(BLUE)AccountIA - Asesor Tributario Inteligente$(RESET)"
	@echo "$(CYAN)Available commands:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Usage examples:$(RESET)"
	@echo "  make setup     # Initial project setup"
	@echo "  make dev       # Start development environment"
	@echo "  make test      # Run all tests"
	@echo "  make deploy    # Deploy to staging"

# ================================
# 🚀 Setup & Environment
# ================================

setup: ## 🔧 Initial project setup (run this first)
	@echo "$(BOLD)$(GREEN)Setting up AccountIA development environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from template...$(RESET)"; \
		cp .env.example .env; \
	fi
	@echo "$(YELLOW)Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE) build
	@echo "$(YELLOW)Starting services...$(RESET)"
	@$(DOCKER_COMPOSE) up -d postgres redis
	@echo "$(YELLOW)Waiting for database to be ready...$(RESET)"
	@sleep 10
	@echo "$(YELLOW)Running database migrations...$(RESET)"
	@make migrate
	@echo "$(YELLOW)Loading initial data...$(RESET)"
	@make seed
	@echo "$(BOLD)$(GREEN)✅ Setup complete! Run 'make dev' to start development.$(RESET)"

clean: ## 🧹 Clean up containers, volumes, and images
	@echo "$(YELLOW)Stopping all containers...$(RESET)"
	@$(DOCKER_COMPOSE) down
	@echo "$(YELLOW)Removing volumes...$(RESET)"
	@docker volume prune -f
	@echo "$(YELLOW)Removing unused images...$(RESET)"
	@docker image prune -f
	@echo "$(GREEN)✅ Cleanup complete!$(RESET)"

reset: clean setup ## 🔄 Complete reset (clean + setup)

# ================================
# 🏃 Development
# ================================

dev: ## 🚀 Start development environment
	@echo "$(BOLD)$(GREEN)Starting AccountIA development environment...$(RESET)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Development environment is running!$(RESET)"
	@echo "$(CYAN)Available services:$(RESET)"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  Admin:     http://localhost:8000/admin"
	@echo "  API Docs:  http://localhost:8000/api/docs"
	@echo "  PgAdmin:   http://localhost:5050"
	@echo "  MailHog:   http://localhost:8025"

stop: ## ⏹️ Stop all services
	@echo "$(YELLOW)Stopping all services...$(RESET)"
	@$(DOCKER_COMPOSE) down

restart: stop dev ## 🔄 Restart all services

logs: ## 📄 Show logs from all services
	@$(DOCKER_COMPOSE) logs -f

logs-backend: ## 📄 Show backend logs
	@$(DOCKER_COMPOSE) logs -f $(BACKEND_CONTAINER)

logs-frontend: ## 📄 Show frontend logs
	@$(DOCKER_COMPOSE) logs -f $(FRONTEND_CONTAINER)

shell-backend: ## 🐚 Open Django shell
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py shell

shell-db: ## 🗄️ Open PostgreSQL shell
	@$(DOCKER_COMPOSE) exec $(DB_CONTAINER) psql -U accountia_user -d accountia_dev

# ================================
# 🗄️ Database Management
# ================================

migrate: ## 🔄 Run database migrations
	@echo "$(YELLOW)Running database migrations...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py migrate

makemigrations: ## 📝 Create new database migrations
	@echo "$(YELLOW)Creating database migrations...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py makemigrations

seed: ## 🌱 Load initial/test data
	@echo "$(YELLOW)Loading initial data...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py loaddata fixtures/initial_users.json
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py loaddata fixtures/tax_rules.json

createsuperuser: ## 👤 Create Django superuser
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py createsuperuser

backup-db: ## 💾 Backup database
	@echo "$(YELLOW)Creating database backup...$(RESET)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec $(DB_CONTAINER) pg_dump -U accountia_user accountia_dev > backups/accountia_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created!$(RESET)"

restore-db: ## 📥 Restore database (usage: make restore-db FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Please specify a backup file: make restore-db FILE=backup.sql$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(RESET)"
	@$(DOCKER_COMPOSE) exec -T $(DB_CONTAINER) psql -U accountia_user -d accountia_dev < $(FILE)
	@echo "$(GREEN)✅ Database restored!$(RESET)"

# ================================
# 🧪 Testing
# ================================

test: ## 🧪 Run all tests
	@echo "$(BOLD)$(GREEN)Running all tests...$(RESET)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)✅ All tests completed!$(RESET)"

test-backend: ## 🧪 Run backend tests
	@echo "$(YELLOW)Running backend tests...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py test

test-frontend: ## 🧪 Run frontend tests
	@echo "$(YELLOW)Running frontend tests...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(FRONTEND_CONTAINER) npm test

test-coverage: ## 📊 Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) coverage run --source='.' manage.py test
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) coverage report
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) coverage html

test-e2e: ## 🎭 Run end-to-end tests
	@echo "$(YELLOW)Running E2E tests...$(RESET)"
	@cd tests/e2e && npm run test:e2e

test-load: ## ⚡ Run load tests
	@echo "$(YELLOW)Running load tests...$(RESET)"
	@cd tests/load && locust --host=http://localhost:8000

# ================================
# 🎨 Code Quality
# ================================

lint: ## 🔍 Run linting for all code
	@echo "$(YELLOW)Running linting...$(RESET)"
	@make lint-backend
	@make lint-frontend

lint-backend: ## 🔍 Run backend linting
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) flake8 .
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) black --check .
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) isort --check-only .
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) mypy .

lint-frontend: ## 🔍 Run frontend linting
	@$(DOCKER_COMPOSE) exec $(FRONTEND_CONTAINER) npm run lint

format: ## ✨ Format all code
	@echo "$(YELLOW)Formatting code...$(RESET)"
	@make format-backend
	@make format-frontend

format-backend: ## ✨ Format backend code
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) black .
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) isort .

format-frontend: ## ✨ Format frontend code
	@$(DOCKER_COMPOSE) exec $(FRONTEND_CONTAINER) npm run format

# ================================
# 🤖 AI & Knowledge Base
# ================================

update-kb: ## 📚 Update AI knowledge base
	@echo "$(YELLOW)Updating AI knowledge base...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py update_knowledge_base
	@echo "$(GREEN)✅ Knowledge base updated!$(RESET)"

test-ai: ## 🧠 Test AI functionality
	@echo "$(YELLOW)Testing AI functionality...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py test_ai_integration

process-documents: ## 📄 Process new documents for AI
	@echo "$(YELLOW)Processing documents for AI...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python scripts/process_documents.py

# ================================
# 📦 Build & Deploy
# ================================

build: ## 🔨 Build all Docker images
	@echo "$(YELLOW)Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE) build

build-prod: ## 🔨 Build production images
	@echo "$(YELLOW)Building production images...$(RESET)"
	@docker-compose -f docker-compose.prod.yml build

deploy-dev: ## 🚀 Deploy to development environment
	@echo "$(YELLOW)Deploying to development...$(RESET)"
	@./scripts/deploy.sh dev

deploy-staging: ## 🚀 Deploy to staging environment
	@echo "$(YELLOW)Deploying to staging...$(RESET)"
	@./scripts/deploy.sh staging

deploy-prod: ## 🚀 Deploy to production environment
	@echo "$(RED)$(BOLD)⚠️  PRODUCTION DEPLOYMENT$(RESET)"
	@echo "Are you sure you want to deploy to production? [y/N]"
	@read -r CONFIRMATION; \
	if [ "$$CONFIRMATION" = "y" ] || [ "$$CONFIRMATION" = "Y" ]; then \
		echo "$(YELLOW)Deploying to production...$(RESET)"; \
		./scripts/deploy.sh prod; \
	else \
		echo "$(GREEN)Deployment cancelled.$(RESET)"; \
	fi

# ================================
# 📊 Monitoring & Health
# ================================

health: ## 🏥 Check health of all services
	@echo "$(YELLOW)Checking service health...$(RESET)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(CYAN)Service endpoints:$(RESET)"
	@curl -s http://localhost:8000/health/ > /dev/null && echo "✅ Backend: healthy" || echo "❌ Backend: unhealthy"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend: healthy" || echo "❌ Frontend: unhealthy"

monitoring: ## 📊 Start monitoring stack (Prometheus + Grafana)
	@echo "$(YELLOW)Starting monitoring stack...$(RESET)"
	@$(DOCKER_COMPOSE) --profile monitoring up -d prometheus grafana
	@echo "$(GREEN)✅ Monitoring stack started!$(RESET)"
	@echo "$(CYAN)Available dashboards:$(RESET)"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3001 (admin/admin)"

# ================================
# 📝 Documentation
# ================================

docs: ## 📖 Generate API documentation
	@echo "$(YELLOW)Generating API documentation...$(RESET)"
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py spectacular --file docs/api/openapi.yaml

docs-serve: ## 📖 Serve documentation locally
	@echo "$(YELLOW)Serving documentation...$(RESET)"
	@cd docs && python -m http.server 8080

# ================================
# 🔧 Utilities
# ================================

install-frontend: ## 📦 Install frontend dependencies
	@$(DOCKER_COMPOSE) exec $(FRONTEND_CONTAINER) npm install

install-backend: ## 📦 Install backend dependencies
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) pip install -r requirements.txt

collectstatic: ## 📦 Collect Django static files
	@$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py collectstatic --noinput

flush-db: ## 🗑️ Flush database (WARNING: Deletes all data)
	@echo "$(RED)$(BOLD)⚠️  This will delete ALL data in the database!$(RESET)"
	@echo "Are you sure? [y/N]"
	@read -r CONFIRMATION; \
	if [ "$$CONFIRMATION" = "y" ] || [ "$$CONFIRMATION" = "Y" ]; then \
		$(DOCKER_COMPOSE) exec $(BACKEND_CONTAINER) python manage.py flush --noinput; \
		echo "$(GREEN)Database flushed.$(RESET)"; \
	else \
		echo "$(GREEN)Operation cancelled.$(RESET)"; \
	fi

# ================================
# 🔍 Debug & Troubleshooting
# ================================

debug: ## 🐛 Show debug information
	@echo "$(BOLD)$(CYAN)AccountIA Debug Information$(RESET)"
	@echo "$(YELLOW)Docker version:$(RESET)"
	@docker --version
	@echo "$(YELLOW)Docker Compose version:$(RESET)"
	@docker-compose --version
	@echo "$(YELLOW)Running containers:$(RESET)"
	@docker ps --filter "name=accountia"
	@echo "$(YELLOW)Container resource usage:$(RESET)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

tail-logs: ## 📄 Tail logs from all services
	@$(DOCKER_COMPOSE) logs -f --tail=100
.PHONY: help install dev dev-backend dev-frontend migrate seed test lint clean docker-up docker-down docker-reset-db reset-db secret-key deploy-check docker-up-all docker-down-all docker-logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -r backend/requirements.txt
	cd frontend && npm install

dev-backend: ## Start backend in development mode
	uvicorn backend.app.main:app --reload --port 8000

dev-frontend: ## Start frontend in development mode
	cd frontend && npm run dev

dev: ## Start both backend and frontend (requires two terminals)
	@echo "Run 'make dev-backend' in one terminal and 'make dev-frontend' in another"

docker-up: ## Start PostgreSQL and Redis
	docker compose up -d postgres redis

docker-up-all: ## Start all services (full stack)
	docker compose up --build -d

docker-down: ## Stop all Docker services
	docker compose down

docker-down-all: ## Stop all services and remove volumes
	docker compose down -v

docker-logs: ## Follow logs from all services
	docker compose logs -f

docker-reset-db: ## Reset PostgreSQL database
	docker compose down -v postgres
	docker compose up -d postgres
	@sleep 3
	alembic upgrade head

migrate: ## Run database migrations
	alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new name="description")
	alembic revision --autogenerate -m "$(name)"

seed: ## Seed the database with test data
	python scripts/seed.py

test: ## Run all tests
	python -m pytest tests/ -v

test-coverage: ## Run tests with coverage report
	python -m pytest tests/ --cov=backend/app --cov-report=term-missing

lint: ## Run linter
	ruff check backend/

deploy-check: ## Run deployment readiness checks
	python scripts/deploy_check.py

clean: ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf frontend/dist

reset-db: ## Reset SQLite database (remove and re-migrate)
	rm -f data/saas.db
	alembic upgrade head

secret-key: ## Generate a secure SECRET_KEY
	python -c "import secrets; print(secrets.token_urlsafe(32))"

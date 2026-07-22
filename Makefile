.PHONY: help install dev test lint format migrate seed check docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements/prod.txt

dev: ## Install dev dependencies
	pip install -r requirements/dev.txt
	pre-commit install 2>/dev/null || true

test: ## Run tests with coverage
	python -m pytest tests/ -v --tb=short --cov=apps --cov=core --cov-report=term-missing

test-fast: ## Run tests without coverage
	python -m pytest tests/ -v --tb=short -x

lint: ## Lint with ruff
	ruff check .
	ruff format --check .

format: ## Format code
	ruff check --fix .
	ruff format .

migrate: ## Run migrations
	python manage.py migrate

seed: ## Seed demo data
	python manage.py seed_demo_data

check: ## Run Django system checks
	python manage.py check
	python manage.py makemigrations --check --dry-run

docker-up: ## Start Docker services
	docker compose up --build -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache staticfiles .coverage

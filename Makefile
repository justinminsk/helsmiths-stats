.PHONY: help test test-python test-frontend lint lint-python lint-frontend format preview analyze snapshot dev build install

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Python / Backend Commands ---

test-python: ## Run Python unit tests
	PYTHONPATH=. pytest tests/

lint-python: ## Run Ruff linter on Python code
	ruff check .

format: ## Run Ruff formatter on Python code
	ruff format .

preview: ## Run the site preview script
	python3 preview_site.py

analyze: ## Run the list analysis script
	python3 analyze_helsmith_lists.py

snapshot: ## Run the snapshot rollover script
	python3 rollover_snapshot.py

# --- Frontend Commands ---

install: ## Install frontend dependencies
	cd frontend && npm install

dev: ## Start the frontend Vite dev server
	cd frontend && npm run dev

build: ## Build the frontend for production
	cd frontend && npm run build

test-frontend: ## Run frontend tests
	cd frontend && npm run test

lint-frontend: ## Run frontend linter
	cd frontend && npm run lint

# --- Aggregate Commands ---

test: test-python test-frontend ## Run all tests (Python and Frontend)

lint: lint-python lint-frontend ## Run all linters (Python and Frontend)

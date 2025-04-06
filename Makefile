.PHONY: setup install test lint run-server help

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
YELLOW=\033[0;33m
GREEN=\033[0;32m
NC=\033[0m # No Color

help: ## Show this help menu
	@echo "Business Finder Makefile Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Setup poetry and install dependencies
	@echo "$(GREEN)Setting up Poetry environment...$(NC)"
	poetry install
	@echo "$(GREEN)Environment ready! Run 'poetry shell' to activate it.$(NC)"

install: ## Install the package in development mode
	@echo "$(GREEN)Installing Business Finder package...$(NC)"
	pip install -e .
	@echo "$(GREEN)Installation complete!$(NC)"

configure: ## Configure your Google API key
	@echo "$(GREEN)Setting up Google API key...$(NC)"
	@echo "Enter your Google API key:"
	@read API_KEY && business-finder config --set-api-key "$$API_KEY"
	@echo "$(GREEN)API key configured!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest
	@echo "$(GREEN)Tests completed!$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest --cov=business_finder --cov-branch --cov-report=term
	@echo "$(GREEN)Coverage test completed!$(NC)"

lint: ## Run linting checks
	@echo "$(GREEN)Running linting checks...$(NC)"
	flake8 .
	black --check business_finder tests
	isort --check business_finder tests
	@echo "$(GREEN)Linting completed!$(NC)"

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	black business_finder tests
	isort business_finder tests
	@echo "$(GREEN)Formatting completed!$(NC)"

run-server: ## Run the web server (default port: 8000)
	@echo "$(GREEN)Starting web server on port 8000...$(NC)"
	@echo "$(GREEN)Access the application at: http://localhost:8000$(NC)"
	python web/server.py

run-server-custom-port: ## Run the web server with a custom port
	@echo "$(GREEN)Enter port number (default: 8000):$(NC)"
	@read PORT && python web/server.py $$PORT

search-example: ## Run a basic search example
	@echo "$(GREEN)Running a basic search for coffee shops in San Francisco...$(NC)"
	business-finder search --search-term "coffee shop" --latitude 37.7749 --longitude -122.4194 --radius 1000
	@echo "$(GREEN)Search complete! Results saved to the data/ directory.$(NC)"

clean: ## Clean temporary files and caches
	@echo "$(GREEN)Cleaning up...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf business_finder/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "$(GREEN)Cleanup complete!$(NC)"
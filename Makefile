.PHONY: test test-local test-features test-conditional test-all coverage \
       lint lint-fix format format-check format-yaml \
       docker-build docker-run docker-push docker-clean \
       ci check clean help

# ============================================================================
# Variables
# ============================================================================

VENV           := venv
PYTHON         := $(VENV)/bin/python3
PIP            := $(VENV)/bin/pip
PYTEST         := $(VENV)/bin/pytest
DOCKER         := docker
IMAGE_NAME     := image-tag-updater
IMAGE_TAG      := latest
DOCKER_IMAGE   := $(IMAGE_NAME):$(IMAGE_TAG)
SRC_DIR        := src
TEST_DIR       := tests

# ============================================================================
# Default
# ============================================================================

.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Virtual Environment
# ============================================================================

venv: $(VENV)/bin/activate ## Create virtualenv and install dev dependencies

$(VENV)/bin/activate: requirements-dev.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	touch $(VENV)/bin/activate
	@echo ""
	@echo "Virtualenv created. To activate:"
	@echo "  source $(VENV)/bin/activate"

# ============================================================================
# Testing
# ============================================================================

test: $(VENV)/bin/activate ## Run unit tests with coverage
	$(PYTEST) $(TEST_DIR)/ -v --cov=$(SRC_DIR) --cov=main --cov-report=term-missing

test-local: $(VENV)/bin/activate ## Run local tests only
	$(PYTHON) $(TEST_DIR)/test_local.py

test-features: $(VENV)/bin/activate ## Run new features tests
	$(PYTHON) $(TEST_DIR)/test_new_features.py

test-conditional: $(VENV)/bin/activate ## Run conditional and summary tests
	$(PYTHON) $(TEST_DIR)/test_conditional_summary.py

test-all: test test-local ## Run all tests (unit + local)

# ============================================================================
# Coverage
# ============================================================================

coverage: $(VENV)/bin/activate ## Generate HTML coverage report
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov=main --cov-report=term-missing --cov-report=html
	@echo "Open htmlcov/index.html in your browser"

# ============================================================================
# Lint & Format
# ============================================================================

lint: $(VENV)/bin/activate ## Run Python linter (ruff)
	$(PYTHON) -m ruff check $(SRC_DIR) main.py $(TEST_DIR)

lint-fix: $(VENV)/bin/activate ## Run Python linter with auto-fix
	$(PYTHON) -m ruff check --fix $(SRC_DIR) main.py $(TEST_DIR)

format: $(VENV)/bin/activate ## Format Python code (ruff)
	$(PYTHON) -m ruff format $(SRC_DIR) main.py $(TEST_DIR)

format-check: $(VENV)/bin/activate ## Check Python code formatting
	$(PYTHON) -m ruff format --check $(SRC_DIR) main.py $(TEST_DIR)

format-yaml: ## Format YAML files with prettier
	npx prettier --write '**/*.yml' '**/*.yaml'

# ============================================================================
# Docker
# ============================================================================

docker-build: ## Build Docker image
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container (dry-run mode)
	$(DOCKER) run --rm $(DOCKER_IMAGE)

docker-push: ## Push Docker image to registry
	$(DOCKER) push $(DOCKER_IMAGE)

docker-clean: ## Remove Docker image
	$(DOCKER) rmi $(DOCKER_IMAGE) 2>/dev/null || true

# ============================================================================
# CI / Quality
# ============================================================================

ci: lint format-check test ## Run full CI pipeline (lint + format-check + test)

check: lint format-check ## Run code quality checks (lint + format-check)

# ============================================================================
# Cleanup
# ============================================================================

clean: ## Remove venv, cache, and build artifacts
	rm -rf $(VENV) .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

.PHONY: help install install-dev test lint format clean run docs

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage
	pytest tests/ -v

lint:  ## Run all linters
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports
	black --check src/ tests/
	isort --check-only src/ tests/

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage

clean-cache:  ## Clear application cache
	rm -rf .cache/
	@echo "Cache cleared"

run:  ## Run analysis with default ticker
	python run_analysis_enhanced.py

run-original:  ## Run original analysis script
	python run_analysis.py

security:  ## Run security checks
	safety check
	bandit -r src/ -f screen

build:  ## Build distribution packages
	python -m build

publish-test:  ## Publish to Test PyPI
	python -m twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m twine upload dist/*

docs-serve:  ## Serve documentation locally
	@echo "Documentation available in docs/ directory"
	@echo "View README.md, ARCHITECTURE.md, CONTRIBUTING.md"

setup-env:  ## Set up development environment
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate     (Windows)"
	@echo "Then run: make install-dev"

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

check:  ## Run all checks (lint + test)
	@make lint
	@make test

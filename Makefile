# csv2yaml project Makefile

.PHONY: help install install-dev install-github test test-verbose test-coverage lint format clean build publish publish-github

help:				## Show this help message
	@echo "csv2yaml - Universal TSV/CSV to YAML converter"
	@echo
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install:			## Install package locally for production use
	uv tool install .

install-github:			## Install package from GitHub
	uv tool install git+https://github.com/HeinrichHartmann/csv2yaml.git

install-dev:			## Install package for development
	uv sync --dev

test:				## Run test suite
	uv run pytest

test-verbose:			## Run test suite with verbose output
	uv run pytest -v -s

test-coverage:			## Run test suite with coverage report
	uv run pytest --cov-report=term-missing --cov-report=html

test-quick:			## Run quick tests only (skip slow tests)
	uv run pytest -m "not slow"

lint:				## Run linting checks
	uv run flake8 csv2yaml tests
	uv run mypy csv2yaml

format:				## Format code with black
	uv run black csv2yaml tests

format-check:			## Check code formatting
	uv run black --check csv2yaml tests

clean:				## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

build:				## Build package
	uv build

publish-test:			## Publish to TestPyPI
	uv publish --repository testpypi

publish:			## Publish to PyPI
	uv publish

publish-github:			## Push to GitHub repository
	git push origin main

# Development workflow commands
dev-setup: install-dev		## Setup development environment
	uv run pre-commit install

dev-test: format lint test	## Run full development test suite

# Example usage commands
example-simple:			## Run example with simple table
	uv run csv2yaml tests/data/named_rows_cols_r1c1.tsv --col-index-dims 1 --row-index-dims 1

example-complex:		## Run example with complex matrix
	uv run csv2yaml tests/data/zamp_matrix_r2c2.tsv --col-index-dims 2 --row-index-dims 2

example-all:			## Run all examples
	@echo "=== Simple Table (r=1,c=1) ==="
	@uv run csv2yaml tests/data/named_rows_cols_r1c1.tsv --col-index-dims 1 --row-index-dims 1
	@echo
	@echo "=== Complex Matrix (r=2,c=2) ==="
	@uv run csv2yaml tests/data/zamp_matrix_r2c2.tsv --col-index-dims 2 --row-index-dims 2
# csv2yaml project Makefile

.PHONY: help clean install test build publish release

help:				## Show this help message
	@echo "csv2yaml - Universal TSV/CSV to YAML converter"
	@echo
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

clean:				## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

install:			## Install package locally
	uv tool install .

test:				## Run test suite
	uv run pytest

build:				## Build wheel and tarball
	uv build

publish:			## Publish package to PyPI
	uv build
	uv publish

release:			## Build package for GitHub release
	uv build
	@echo "Built package files:"
	@ls -la dist/
	@echo ""
	@echo "To create GitHub release:"
	@echo "1. git tag v0.1.0"
	@echo "2. git push origin v0.1.0"
	@echo "3. Create release on GitHub and upload files from dist/"
	@echo ""
	@echo "Users can then install with:"
	@echo "uv tool install https://github.com/HeinrichHartmann/csv2yaml/releases/download/v0.1.0/csv2yaml-0.1.0-py3-none-any.whl"
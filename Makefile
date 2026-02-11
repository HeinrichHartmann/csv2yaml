# csv2yaml project Makefile

.PHONY: help clean install test publish

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

install:			## Install package from GitHub
	uv tool install git+https://github.com/HeinrichHartmann/csv2yaml.git

test:				## Run test suite
	uv run pytest

publish:			## Push to GitHub repository
	git push origin main
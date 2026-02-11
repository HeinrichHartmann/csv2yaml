# csv2yaml project Makefile

.PHONY: help clean install test build publish release gh-release

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

gh-release:			## Automated GitHub release with gh CLI
	@command -v gh >/dev/null 2>&1 || { echo "Error: gh CLI not found. Install with: brew install gh" >&2; exit 1; }
	@echo "Creating automated GitHub release..."
	uv build
	git tag v0.1.0 || echo "Tag v0.1.0 already exists"
	gh release create v0.1.0 dist/* \
		--title "csv2yaml v0.1.0 - Universal TSV to YAML Converter" \
		--notes "🎉 **csv2yaml v0.1.0** - Universal TSV/CSV to YAML converter with multi-dimensional index support\n\n## Installation\n\`\`\`bash\n# Install from release wheel\nuv tool install https://github.com/HeinrichHartmann/csv2yaml/releases/download/v0.1.0/csv2yaml-0.1.0-py3-none-any.whl\n\`\`\`\n\n## Features\n✅ Multi-dimensional indices (r×c dimensions)\n✅ LLM-optimized YAML output\n✅ Pandas-powered CSV parsing\n✅ Rich CLI with beautiful output\n✅ Comprehensive test coverage (21/21 tests)\n\n## Quick Start\n\`\`\`bash\n# Simple table\ncsv2yaml data.csv --col-index-dims 1 --row-index-dims 1\n\n# Complex matrix\ncsv2yaml matrix.tsv --col-index-dims 2 --row-index-dims 2\n\`\`\`"
	@echo ""
	@echo "✅ GitHub release created successfully!"
	@echo "Users can install with:"
	@echo "uv tool install https://github.com/HeinrichHartmann/csv2yaml/releases/download/v0.1.0/csv2yaml-0.1.0-py3-none-any.whl"
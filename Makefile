# csv2yaml project Makefile

.PHONY: help clean install test build publish release gh-release bump-version

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
	$(eval VERSION := $(shell python3 -c "import re; content=open('pyproject.toml').read(); print(re.search(r'version = \"([^\"]+)\"', content).group(1))"))
	@echo "Creating GitHub release v$(VERSION)..."
	uv build
	git tag v$(VERSION) || echo "Tag v$(VERSION) already exists"
	git push origin v$(VERSION) || echo "Tag already pushed"
	gh release create v$(VERSION) dist/* \
		--title "csv2yaml v$(VERSION) - Universal TSV to YAML Converter" \
		--notes "🎉 **csv2yaml v$(VERSION)** - Universal TSV/CSV to YAML converter with multi-dimensional index support\n\n## Installation\n\`\`\`bash\n# Install from release wheel\nuv tool install https://github.com/HeinrichHartmann/csv2yaml/releases/download/v$(VERSION)/csv2yaml-$(VERSION)-py3-none-any.whl\n\`\`\`\n\n## Features\n✅ Multi-dimensional indices (r×c dimensions)\n✅ LLM-optimized YAML output\n✅ Pandas-powered CSV parsing\n✅ Rich CLI with beautiful output\n✅ Comprehensive test coverage (21/21 tests)\n\n## Quick Start\n\`\`\`bash\n# Simple table\ncsv2yaml data.csv --col-index-dims 1 --row-index-dims 1\n\n# Complex matrix\ncsv2yaml matrix.tsv --col-index-dims 2 --row-index-dims 2\n\`\`\`"
	@echo ""
	@echo "✅ GitHub release v$(VERSION) created successfully!"
	@echo "Users can install with:"
	@echo "uv tool install https://github.com/HeinrichHartmann/csv2yaml/releases/download/v$(VERSION)/csv2yaml-$(VERSION)-py3-none-any.whl"
	$(MAKE) bump-version

bump-version:			## Increment minor version after release
	@echo "Incrementing version..."
	@python3 -c "import re; content=open('pyproject.toml').read(); match=re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"', content); major,minor,patch=map(int,match.groups()); new_version=f'{major}.{minor+1}.0'; new_content=re.sub(r'version = \"(\d+)\.(\d+)\.(\d+)\"', f'version = \"{new_version}\"', content); open('pyproject.toml','w').write(new_content); print(f'Version bumped to {new_version}')"
	@git add pyproject.toml
	$(eval NEW_VERSION := $(shell python3 -c "import re; content=open('pyproject.toml').read(); print(re.search(r'version = \"([^\"]+)\"', content).group(1))"))
	@git commit -m "Bump version to $(NEW_VERSION)"
	@echo "Version incremented to $(NEW_VERSION) and committed"
# csv2yaml

Universal TSV/CSV to YAML converter with multi-dimensional index support.

## Why csv2yaml?

Existing tools (yq, Miller) only handle flat tables. **csv2yaml** converts complex spreadsheet structures into LLM-friendly YAML format while preserving hierarchical relationships.

Perfect for:
- Complex matrices with multi-level headers
- Spreadsheets with grouped sections
- Converting Google Sheets for LLM processing
- Data analysis workflows requiring nested structures

## Installation

```bash
# Install globally with uv
uv tool install csv2yaml

# Or install in project
uv add csv2yaml
```

## Quick Start

```bash
# Simple table (1×1 indices)
csv2yaml data.csv

# Complex matrix (2×2 indices, like ZAMP matrix)
csv2yaml matrix.tsv --col-index-dims 2 --row-index-dims 2 -o output.yaml
```

## Examples

### Simple Table (r=1, c=1)

**Input:**
```tsv
	Age	City
Alice	25	NYC
Bob	30	LA
```

**Output:**
```yaml
meta:
  dimensions: {col_index_dims: 1, row_index_dims: 1}

data:
  - Alice:
      Age: 25
      City: NYC
  - Bob:
      Age: 30
      City: LA
```

### Complex Matrix (r=2, c=2)

**Input:**
```tsv
Categories	Components	Competitor Stacks		Cloud Providers
		Booking.com	ASOS	AWS	GCP
Data Mgmt	Sources	Kafka	Azure DL	S3	BigQuery
	Features	Internal	Cosmos DB	SageMaker	Vertex AI
```

**Output:**
```yaml
meta:
  source_file: "matrix.tsv"
  dimensions:
    col_index_dims: 2
    row_index_dims: 2

data:
  - "Data Mgmt":
      "Sources":
        "Booking.com": "Kafka"
        "ASOS": "Azure DL"
        "AWS": "S3"
        "GCP": "BigQuery"
      "Features":
        "Booking.com": "Internal"
        "ASOS": "Cosmos DB"
        "AWS": "SageMaker"
        "GCP": "Vertex AI"
```

## CLI Options

```bash
csv2yaml input.tsv [OPTIONS]

Options:
  --col-index-dims INTEGER    Column header levels (default: 1)
  --row-index-dims INTEGER    Row header levels (default: 1)
  --output, -o PATH          Output YAML file
  --separator, -s TEXT       Field separator (auto-detected)
  --skip-empty-cells         Skip empty cells (default: true)
  --preserve-types           Keep numbers as numbers
  --verbose, -v              Verbose output
  --help                     Show help message
```

## Use Cases

- **LLM Data Preparation:** Convert complex spreadsheets for AI processing
- **Data Analysis:** Transform matrices into structured formats
- **Configuration Management:** Convert tabular config to YAML
- **Documentation:** Make spreadsheet data more readable

## Features

✅ **Multi-dimensional indices** - Handle complex header structures
✅ **LLM-optimized output** - Named hierarchies eliminate column counting
✅ **Universal design** - Works with any TSV/CSV complexity
✅ **Metadata included** - Context about source and dimensions
✅ **Pandas-powered** - Robust CSV parsing with edge case handling
✅ **Rich CLI** - Beautiful terminal output and progress indicators

## Development

See [docs/ADR-001](docs/ADR-001-multi-dimensional-tsv-to-yaml.md) for architecture details.

```bash
# Setup development environment
git clone <repo>
cd csv2yaml
uv sync --dev

# Run tests
uv run pytest

# Install locally
uv tool install .
```

## License

MIT License - see [LICENSE](LICENSE) for details.
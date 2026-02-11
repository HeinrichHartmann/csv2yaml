# ADR-001: Multi-Dimensional TSV to YAML Converter

**Status:** Proposed
**Date:** 2026-02-11
**Deciders:** ZAMP Project Team

## Context

Large Language Models (LLMs) struggle with complex TSV/CSV structures that have multi-dimensional headers and indices. Existing tools (yq, Miller, basic CSV converters) only handle flat, single-header tables.

**Problem:** No tool exists that can convert complex spreadsheet structures into LLM-friendly formats while preserving hierarchical relationships.

**Use Case:** ZAMP ML Technology Comparison Matrix with 2D headers and complex nested structure.

## Decision

Build a **universal TSV to YAML converter** with configurable multi-dimensional index support.

```bash
csv2yaml input.tsv --col-index-dims 2 --row-index-dims 2 --output matrix.yaml
```

## Output Format

### Meta + Data Structure

All outputs include metadata and hierarchically structured data:

```yaml
meta:
  source_file: "matrix.tsv"
  dimensions:
    total_rows: 31
    total_cols: 20
    col_index_dims: 2
    row_index_dims: 2
    data_rows: 29
    data_cols: 18

data:
  # Hierarchical structure based on index dimensions
```

### Index Dimension Examples

#### r=0, c=1 (Simple List)
Input TSV:
```
Name	Age	City
Alice	25	NYC
Bob	30	LA
```

Output:
```yaml
meta:
  dimensions: {total_rows: 3, total_cols: 3, col_index_dims: 1, row_index_dims: 0}

data:
  - row[1]:
      Name: Alice
      Age: 25
      City: NYC
  - row[2]:
      Name: Alice
      Age: 30
      City: LA
```

#### r=1, c=1 (Named Rows + Named Columns)
Input TSV:
```
	Age	City
Alice	25	NYC
Bob	30	LA
```

Output:
```yaml
meta:
  dimensions: {total_rows: 3, total_cols: 3, col_index_dims: 1, row_index_dims: 1}

data:
  - Alice:
      Age: 25
      City: NYC
  - Bob:
      Age: 30
      City: LA
```

#### r=1, c=2 (Named Rows + Nested Column Hierarchy)
Input TSV:
```
	Personal		Work
	Age	City	Company	Role
Alice	25	NYC	Acme	Engineer
Bob	30	LA	Beta	Manager
```

Output:
```yaml
meta:
  dimensions: {total_rows: 3, total_cols: 5, col_index_dims: 2, row_index_dims: 1}

data:
  - Alice:
      Personal:
        Age: 25
        City: NYC
      Work:
        Company: Acme
        Role: Engineer
  - Bob:
      Personal:
        Age: 30
        City: LA
      Work:
        Company: Beta
        Role: Manager
```

#### r=2, c=2 (Full Nested Hierarchy)
Input TSV:
```
	Personal		Work
Team	Member	Age	City	Company	Role
Alpha	Alice	25	NYC	Acme	Engineer
Alpha	Bob	30	LA	Beta	Manager
Beta	Carol	35	SF	Gamma	Director
```

Output:
```yaml
meta:
  dimensions: {total_rows: 4, total_cols: 6, col_index_dims: 2, row_index_dims: 2}

data:
  - Alpha:
      Alice:
        Personal:
          Age: 25
          City: NYC
        Work:
          Company: Acme
          Role: Engineer
      Bob:
        Personal:
          Age: 30
          City: LA
        Work:
          Company: Beta
          Role: Manager
  - Beta:
      Carol:
        Personal:
          Age: 35
          City: SF
        Work:
          Company: Gamma
          Role: Director
```

### ZAMP Matrix Example (r=2, c=2)

Input: Complex ML technology matrix
```
Categories	Component Types	Zalando Examples	Competitor Stacks		Cloud Provider Stacks	Vendor Stacks
			Booking.com	ASOS	AWS SageMaker	Databricks	ZenML
1. Data Management	Data Sources	Kafka, BigQuery	Internal APIs	Azure Data Lake	S3	Unity Catalog	External integrations
	Feature Stores	Hopsworks	Feature Store	Cosmos DB	SageMaker FS	Feature Store	Feast/Tecton
```

Output:
```yaml
meta:
  source_file: "zamp_matrix.tsv"
  dimensions:
    total_rows: 4
    total_cols: 7
    col_index_dims: 2
    row_index_dims: 2

data:
  - "1. Data Management":
      "Data Sources":
        "Booking.com": "Internal APIs"
        "ASOS": "Azure Data Lake"
        "AWS SageMaker": "S3"
        "Databricks": "Unity Catalog"
        "ZenML": "External integrations"
      "Feature Stores":
        "Booking.com": "Feature Store"
        "ASOS": "Cosmos DB"
        "AWS SageMaker": "SageMaker FS"
        "Databricks": "Feature Store"
        "ZenML": "Feast/Tecton"
```

## CLI Interface

```bash
# Simple table (r=1, c=1)
csv2yaml data.csv --col-index-dims 1 --row-index-dims 1

# Complex matrix (r=2, c=2)
csv2yaml matrix.tsv --col-index-dims 2 --row-index-dims 2 -o output.yaml

# Skip empty cells, preserve types
csv2yaml data.tsv --skip-empty-cells --preserve-types
```

## Benefits

1. **LLM-Friendly:** Eliminates column counting errors with named hierarchies
2. **Universal:** Works with any complexity level (1×1 to N×M dimensions)
3. **Semantic Preservation:** Maintains relationships from source structure
4. **Metadata Included:** Context about dimensions and source for debugging
5. **Flexible:** Configurable index dimensions for any use case

---
**Decision Status:** ✅ **APPROVED** - Proceeding with implementation
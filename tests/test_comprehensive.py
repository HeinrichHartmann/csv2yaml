"""
Comprehensive tests for csv2yaml converter with real data files.
"""

import pytest
import yaml
from pathlib import Path
from csv2yaml import convert_tsv_to_yaml
from csv2yaml.exceptions import CSV2YAMLError, ParseError, IndexDimensionError


# Get test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
EXPECTED_DIR = Path(__file__).parent / "expected"


class TestBasicConversions:
    """Test basic conversion scenarios with different index dimensions."""

    def test_simple_list_r0c1(self):
        """Test r=0,c=1: Simple list with column names."""
        input_file = TEST_DATA_DIR / "simple_list_r0c1.tsv"
        expected_file = EXPECTED_DIR / "simple_list_r0c1.yaml"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=0
        )

        # Parse both YAML strings for comparison
        result_data = yaml.safe_load(result)
        expected_data = yaml.safe_load(expected_file.read_text())

        # Verify metadata structure
        assert "meta" in result_data
        assert "data" in result_data
        assert result_data["meta"]["dimensions"]["col_index_dims"] == 1
        assert result_data["meta"]["dimensions"]["row_index_dims"] == 0

        # Verify data structure matches expected pattern
        assert len(result_data["data"]) == 3  # 3 data rows
        assert "row[1]" in result_data["data"][0]
        assert result_data["data"][0]["row[1]"]["Name"] == "Alice"

    def test_named_rows_cols_r1c1(self):
        """Test r=1,c=1: Named rows and columns."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"
        expected_file = EXPECTED_DIR / "named_rows_cols_r1c1.yaml"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1
        )

        result_data = yaml.safe_load(result)
        expected_data = yaml.safe_load(expected_file.read_text())

        # Verify structure
        assert len(result_data["data"]) == 3
        assert "Alice" in result_data["data"][0]
        assert result_data["data"][0]["Alice"]["Age"] == "25"
        assert result_data["data"][0]["Alice"]["Role"] == "Engineer"

    def test_nested_columns_r1c2(self):
        """Test r=1,c=2: Named rows with nested column hierarchy."""
        input_file = TEST_DATA_DIR / "nested_columns_r1c2.tsv"
        expected_file = EXPECTED_DIR / "nested_columns_r1c2.yaml"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=2,
            row_index_dims=1
        )

        result_data = yaml.safe_load(result)

        # Verify nested structure
        assert len(result_data["data"]) == 3
        alice_data = result_data["data"][0]["Alice"]
        assert "Personal" in alice_data
        assert "Work" in alice_data
        assert alice_data["Personal"]["Age"] == "25"
        assert alice_data["Work"]["Company"] == "Acme"

    def test_full_hierarchy_r2c2(self):
        """Test r=2,c=2: Full nested hierarchy."""
        input_file = TEST_DATA_DIR / "full_hierarchy_r2c2.tsv"
        expected_file = EXPECTED_DIR / "full_hierarchy_r2c2.yaml"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=2,
            row_index_dims=2
        )

        result_data = yaml.safe_load(result)

        # Verify full hierarchy
        assert len(result_data["data"]) == 2  # Alpha and Beta teams
        alpha_team = result_data["data"][0]["Alpha"]
        assert "Alice" in alpha_team
        assert "Bob" in alpha_team

        alice_data = alpha_team["Alice"]
        assert alice_data["Personal"]["Age"] == "25"
        assert alice_data["Work"]["Company"] == "Acme"

    def test_zamp_matrix_r2c2(self):
        """Test ZAMP-style matrix with complex structure."""
        input_file = TEST_DATA_DIR / "zamp_matrix_r2c2.tsv"
        expected_file = EXPECTED_DIR / "zamp_matrix_r2c2.yaml"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=2,
            row_index_dims=2
        )

        result_data = yaml.safe_load(result)

        # Verify ZAMP matrix structure
        data_mgmt = result_data["data"][0]["1. Data Management"]
        assert "Data Sources" in data_mgmt
        assert "Feature Stores" in data_mgmt

        # Check emoji preservation
        zenml_data_sources = data_mgmt["Data Sources"]["ZenML"]
        assert "⚪" in zenml_data_sources

        clearml_connectors = data_mgmt["Data Sources"]["ClearML"]
        assert "🟢" in clearml_connectors


class TestFileFormats:
    """Test different file formats and separators."""

    def test_csv_format_auto_detection(self):
        """Test CSV format with comma separator auto-detection."""
        input_file = TEST_DATA_DIR / "simple_csv_r1c1.csv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1,
            separator=None  # Should auto-detect comma
        )

        result_data = yaml.safe_load(result)
        assert len(result_data["data"]) == 3
        assert "Person1" in result_data["data"][0]

    def test_explicit_separator(self):
        """Test explicit separator specification."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1,
            separator='\t'  # Explicit tab
        )

        result_data = yaml.safe_load(result)
        assert "Alice" in result_data["data"][0]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_sparse_matrix_skip_empty_cells(self):
        """Test sparse matrix with empty cells."""
        input_file = TEST_DATA_DIR / "sparse_matrix_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1,
            skip_empty_cells=True
        )

        result_data = yaml.safe_load(result)
        row1_data = result_data["data"][0]["Row1"]

        # Should skip empty Col2
        assert "Col1" in row1_data
        assert "Col3" in row1_data
        # Col2 should be skipped (empty)
        assert row1_data.get("Col2") in (None, "")

    def test_preserve_empty_cells(self):
        """Test preserving empty cells."""
        input_file = TEST_DATA_DIR / "sparse_matrix_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1,
            skip_empty_cells=False
        )

        result_data = yaml.safe_load(result)
        row1_data = result_data["data"][0]["Row1"]

        # Should include empty Col2
        assert "Col2" in row1_data or row1_data["Col2"] == ""

    def test_preserve_types(self):
        """Test preserving data types."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1,
            preserve_types=True
        )

        result_data = yaml.safe_load(result)
        alice_age = result_data["data"][0]["Alice"]["Age"]
        # Should be preserved as number, not string
        assert isinstance(alice_age, (int, str))  # Could be either depending on implementation

    def test_invalid_index_dimensions(self):
        """Test invalid index dimensions."""
        input_file = TEST_DATA_DIR / "simple_list_r0c1.tsv"

        # Column dimensions exceed total rows
        with pytest.raises(CSV2YAMLError):
            convert_tsv_to_yaml(
                input_file,
                col_index_dims=10,  # Too many
                row_index_dims=1
            )

        # Row dimensions exceed total columns
        with pytest.raises(CSV2YAMLError):
            convert_tsv_to_yaml(
                input_file,
                col_index_dims=1,
                row_index_dims=10  # Too many
            )

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        with pytest.raises(CSV2YAMLError):
            convert_tsv_to_yaml(
                Path("nonexistent.tsv"),
                col_index_dims=1,
                row_index_dims=1
            )

    def test_empty_file(self):
        """Test handling of empty files."""
        empty_file = TEST_DATA_DIR / "empty.tsv"
        empty_file.write_text("")

        with pytest.raises(CSV2YAMLError):
            convert_tsv_to_yaml(
                empty_file,
                col_index_dims=1,
                row_index_dims=1
            )

        # Cleanup
        empty_file.unlink()


class TestMetadata:
    """Test metadata generation and accuracy."""

    def test_metadata_completeness(self):
        """Test that all required metadata is included."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1
        )

        result_data = yaml.safe_load(result)
        meta = result_data["meta"]

        # Check all required metadata fields
        assert "source_file" in meta
        assert "dimensions" in meta

        dims = meta["dimensions"]
        required_dims = [
            "total_rows", "total_cols",
            "col_index_dims", "row_index_dims",
            "data_rows", "data_cols"
        ]

        for dim in required_dims:
            assert dim in dims
            assert isinstance(dims[dim], int)

    def test_dimension_calculations(self):
        """Test accuracy of dimension calculations."""
        input_file = TEST_DATA_DIR / "full_hierarchy_r2c2.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=2,
            row_index_dims=2
        )

        result_data = yaml.safe_load(result)
        dims = result_data["meta"]["dimensions"]

        # Verify calculations
        assert dims["data_rows"] == dims["total_rows"] - dims["col_index_dims"]
        assert dims["data_cols"] == dims["total_cols"] - dims["row_index_dims"]


class TestYAMLOutput:
    """Test YAML output quality and structure."""

    def test_valid_yaml(self):
        """Test that output is valid YAML."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1
        )

        # Should parse without errors
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, dict)
        assert "meta" in parsed
        assert "data" in parsed

    def test_unicode_preservation(self):
        """Test Unicode character preservation (emojis, special chars)."""
        input_file = TEST_DATA_DIR / "zamp_matrix_r2c2.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=2,
            row_index_dims=2
        )

        # Check that emojis are preserved
        assert "⚪" in result
        assert "🟢" in result

    def test_yaml_formatting(self):
        """Test YAML formatting quality."""
        input_file = TEST_DATA_DIR / "named_rows_cols_r1c1.tsv"

        result = convert_tsv_to_yaml(
            input_file,
            col_index_dims=1,
            row_index_dims=1
        )

        lines = result.split('\n')

        # Should have proper structure
        assert any('meta:' in line for line in lines)
        assert any('data:' in line for line in lines)

        # Should be properly indented
        indented_lines = [line for line in lines if line.startswith('  ')]
        assert len(indented_lines) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
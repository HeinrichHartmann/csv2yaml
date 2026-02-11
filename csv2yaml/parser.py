"""
TSV/CSV parser with multi-dimensional index support.

Uses pandas for robust CSV parsing and handles complex header structures.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import pandas as pd

from .exceptions import ParseError, IndexDimensionError


@dataclass
class ParsedData:
    """Container for parsed TSV data with metadata."""
    meta: Dict[str, Any]
    data: List[Dict[str, Any]]


class TSVParser:
    """
    Parser for TSV/CSV files with multi-dimensional index support.

    Leverages pandas for robust CSV parsing and handles hierarchical headers.
    """

    def __init__(
        self,
        col_index_dims: int = 1,
        row_index_dims: int = 1,
        separator: str = '\t',
        verbose: bool = False
    ):
        self.col_index_dims = col_index_dims
        self.row_index_dims = row_index_dims
        self.separator = separator
        self.verbose = verbose

    def parse_file(self, input_file: Path) -> ParsedData:
        """
        Parse a TSV/CSV file into structured data.

        Args:
            input_file: Path to input file

        Returns:
            ParsedData with metadata and hierarchically structured data

        Raises:
            ParseError: If file cannot be read or parsed
            IndexDimensionError: If index dimensions exceed data dimensions
        """
        try:
            # Read the raw file with pandas
            # First, determine the maximum number of columns
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                max_cols = max(len(line.rstrip('\n').split(self.separator)) for line in lines if line.strip())

            df = pd.read_csv(
                input_file,
                sep=self.separator,
                header=None,  # We'll handle headers manually
                keep_default_na=False,  # Preserve empty strings
                dtype=str,  # Keep everything as strings initially
                names=list(range(max_cols))  # Use column indices as names
            )

            if self.verbose:
                print(f"Read {len(df)} rows × {len(df.columns)} columns")

            # Validate dimensions
            if self.col_index_dims > len(df):
                raise IndexDimensionError(
                    f"Column index dimensions ({self.col_index_dims}) exceed "
                    f"total rows ({len(df)})"
                )

            if self.row_index_dims > len(df.columns):
                raise IndexDimensionError(
                    f"Row index dimensions ({self.row_index_dims}) exceed "
                    f"total columns ({len(df.columns)})"
                )

            # Extract metadata
            meta = {
                "source_file": str(input_file),
                "dimensions": {
                    "total_rows": len(df),
                    "total_cols": len(df.columns),
                    "col_index_dims": self.col_index_dims,
                    "row_index_dims": self.row_index_dims,
                    "data_rows": len(df) - self.col_index_dims,
                    "data_cols": len(df.columns) - self.row_index_dims,
                }
            }

            # Parse the structure based on index dimensions
            data = self._parse_structure(df)

            return ParsedData(meta=meta, data=data)

        except Exception as e:
            if isinstance(e, (ParseError, IndexDimensionError)):
                raise
            raise ParseError(f"Failed to parse {input_file}: {e}") from e

    def _parse_structure(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Parse the DataFrame into hierarchical structure based on index dimensions.

        This is where the magic happens - converting flat TSV into nested YAML structure.
        """
        # Store original df for column header extraction
        self._original_df = df.copy()

        # Extract column headers from the top rows
        col_headers = []
        for i in range(self.col_index_dims):
            header_row = df.iloc[i, self.row_index_dims:].fillna('').tolist()
            col_headers.append(header_row)

        # For debugging - let's also get the full headers to understand the structure
        if self.verbose:
            for i in range(self.col_index_dims):
                full_header = df.iloc[i].fillna('').tolist()
                print(f"Full header row {i}: {full_header}")
                print(f"Data header row {i}: {col_headers[i]}")

        # Extract row headers from the left columns
        row_headers = []
        for j in range(self.row_index_dims):
            header_col = df.iloc[self.col_index_dims:, j].fillna('').tolist()
            row_headers.append(header_col)

        # Get data portion (excluding headers)
        data_rows = df.iloc[self.col_index_dims:, self.row_index_dims:].values.tolist()

        # Build result based on row index dimensions
        result = []

        if self.row_index_dims == 0:
            # r=0: Use row[1], row[2], etc.
            for i, data_row in enumerate(data_rows):
                row_data = self._build_column_data(col_headers, data_row)
                result.append({f"row[{i+1}]": row_data})

        elif self.row_index_dims == 1:
            # r=1: Use first column as row names
            for i, row_name in enumerate(row_headers[0]):
                row_data = self._build_column_data(col_headers, data_rows[i])
                result.append({row_name: row_data})

        elif self.row_index_dims == 2:
            # r=2: Two-level row hierarchy
            groups = {}
            for i, (level1, level2) in enumerate(zip(row_headers[0], row_headers[1])):
                if level1 not in groups:
                    groups[level1] = {}
                row_data = self._build_column_data(col_headers, data_rows[i])
                groups[level1][level2] = row_data

            for group_name, group_data in groups.items():
                result.append({group_name: group_data})

        return result

    def _build_column_data(self, col_headers: List[List[str]], data_row: List[str]) -> Dict[str, Any]:
        """Build nested column data structure for a single row."""
        if self.col_index_dims == 1:
            # c=1: Simple mapping
            return dict(zip(col_headers[0], data_row))

        elif self.col_index_dims == 2:
            # c=2: Two-level column hierarchy
            # Need to reconstruct proper level1 headers by looking at original headers
            full_level1_headers = self._original_df.iloc[0].fillna('').tolist()
            level2_headers = col_headers[1]  # Already extracted correctly

            result = {}
            current_level1 = None

            # First, build a mapping of which level1 header each data column belongs to
            level1_mapping = []

            for data_col_idx in range(len(level2_headers)):
                # Map back to original column index
                orig_col_idx = data_col_idx + self.row_index_dims

                # Find the appropriate level1 header by looking backwards from this position
                level1_header = None
                for j in range(orig_col_idx, -1, -1):
                    if j < len(full_level1_headers) and full_level1_headers[j].strip():
                        level1_header = full_level1_headers[j]
                        break

                level1_mapping.append(level1_header)

            if self.verbose:
                print(f"Level1 mapping: {level1_mapping}")
                print(f"Level2 headers: {level2_headers}")

            # Now process each data column
            for i, (level2_header, value) in enumerate(zip(level2_headers, data_row)):
                # Get the level1 header for this column
                level1_header = level1_mapping[i] if i < len(level1_mapping) else None

                # Initialize the level1 group if not exists
                if level1_header and level1_header not in result:
                    result[level1_header] = {}

                # Add the data to the appropriate group
                if level1_header and level2_header.strip():
                    result[level1_header][level2_header] = value

            return result

        # For higher dimensions, use generic approach
        return dict(zip(col_headers[-1], data_row))
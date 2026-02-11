"""
Main converter function for csv2yaml.

Orchestrates the parsing and serialization process.
"""

from pathlib import Path
from typing import Optional

from .parser import TSVParser
from .serializer import YAMLSerializer


def convert_tsv_to_yaml(
    input_file: Path,
    col_index_dims: int = 1,
    row_index_dims: int = 1,
    separator: str = '\t',
    skip_empty_cells: bool = True,
    preserve_types: bool = False,
    verbose: bool = False,
) -> str:
    """
    Convert a TSV/CSV file to YAML format with multi-dimensional index support.

    Args:
        input_file: Path to input TSV/CSV file
        col_index_dims: Number of header rows for column indices
        row_index_dims: Number of header columns for row indices
        separator: Field separator character
        skip_empty_cells: Skip empty cells in output
        preserve_types: Preserve data types instead of converting to strings
        verbose: Enable verbose output

    Returns:
        YAML string representation of the data

    Raises:
        ParseError: If the input file cannot be parsed
        IndexDimensionError: If index dimensions are invalid
        SerializationError: If YAML serialization fails
    """

    # Parse the TSV file
    parser = TSVParser(
        col_index_dims=col_index_dims,
        row_index_dims=row_index_dims,
        separator=separator,
        verbose=verbose
    )

    parsed_data = parser.parse_file(input_file)

    # Serialize to YAML
    serializer = YAMLSerializer(
        skip_empty_cells=skip_empty_cells,
        preserve_types=preserve_types,
        verbose=verbose
    )

    return serializer.serialize(parsed_data)
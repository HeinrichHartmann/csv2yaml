"""
CLI interface for csv2yaml converter.

Provides command-line interface for converting TSV/CSV files to YAML format
with support for multi-dimensional indices.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import track
from rich.panel import Panel

from .converter import convert_tsv_to_yaml
from .exceptions import CSV2YAMLError

console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--col-index-dims',
    default=1,
    help='Number of header rows to treat as hierarchical column indices (default: 1)'
)
@click.option(
    '--row-index-dims',
    default=1,
    help='Number of header columns to treat as hierarchical row indices (default: 1)'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output YAML file path (default: stdout)'
)
@click.option(
    '--separator', '-s',
    default=None,
    help='Field separator character. Auto-detected if not specified (\\t for .tsv, , for .csv)'
)
@click.option(
    '--skip-empty-cells',
    is_flag=True,
    default=True,
    help='Skip empty cells in output (default: True)'
)
@click.option(
    '--preserve-types',
    is_flag=True,
    default=False,
    help='Preserve data types (numbers, booleans) instead of converting to strings'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Verbose output'
)
@click.version_option()
def main(
    input_file: Path,
    col_index_dims: int,
    row_index_dims: int,
    output: Optional[Path],
    separator: Optional[str],
    skip_empty_cells: bool,
    preserve_types: bool,
    verbose: bool,
) -> None:
    """
    Convert TSV/CSV files to YAML with multi-dimensional index support.

    This tool converts complex spreadsheet structures into LLM-friendly YAML format
    while preserving hierarchical relationships.

    Examples:

        # Simple conversion (1×1 indices)
        csv2yaml data.csv -o output.yaml

        # Complex matrix (2×2 indices, like ZAMP matrix)
        csv2yaml matrix.tsv --col-index-dims 2 --row-index-dims 2 -o matrix.yaml

        # Process and output to stdout
        csv2yaml data.tsv --col-index-dims 1 --row-index-dims 2
    """

    if verbose:
        console.print(Panel.fit(
            f"[bold blue]csv2yaml v0.1.0[/bold blue]\n\n"
            f"Input: {input_file}\n"
            f"Column index dimensions: {col_index_dims}\n"
            f"Row index dimensions: {row_index_dims}\n"
            f"Output: {'stdout' if output is None else output}\n"
            f"Separator: {'auto-detect' if separator is None else repr(separator)}",
            title="Configuration"
        ))

    try:
        # Auto-detect separator if not provided
        if separator is None:
            if input_file.suffix.lower() == '.tsv':
                separator = '\t'
            elif input_file.suffix.lower() == '.csv':
                separator = ','
            else:
                separator = '\t'  # Default to tab

        if verbose:
            console.print(f"[dim]Using separator: {repr(separator)}[/dim]")

        # Convert the file
        yaml_output = convert_tsv_to_yaml(
            input_file,
            col_index_dims=col_index_dims,
            row_index_dims=row_index_dims,
            separator=separator,
            skip_empty_cells=skip_empty_cells,
            preserve_types=preserve_types,
            verbose=verbose
        )

        # Output results
        if output is None:
            console.print(yaml_output)
        else:
            output.write_text(yaml_output, encoding='utf-8')
            if verbose:
                console.print(f"[green]✓[/green] Successfully wrote YAML to {output}")

    except CSV2YAMLError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == '__main__':
    main()
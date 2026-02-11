"""
csv2yaml: Universal TSV/CSV to YAML converter with multi-dimensional index support.

A tool designed to convert complex spreadsheet structures into LLM-friendly YAML format
while preserving hierarchical relationships and semantic meaning.
"""

__version__ = "0.1.0"
__author__ = "ZAMP Project Team"

from .parser import TSVParser
from .serializer import YAMLSerializer
from .converter import convert_tsv_to_yaml

__all__ = [
    "TSVParser",
    "YAMLSerializer",
    "convert_tsv_to_yaml",
]
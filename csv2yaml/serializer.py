"""
YAML serializer for parsed TSV data.

Converts parsed hierarchical data into LLM-friendly YAML format.
"""

from typing import Any, Dict, List
import yaml

from .parser import ParsedData
from .exceptions import SerializationError


class YAMLSerializer:
    """
    Serializer for converting parsed data to YAML format.

    Optimized for LLM consumption with clean, readable structure.
    """

    def __init__(
        self,
        skip_empty_cells: bool = True,
        preserve_types: bool = False,
        verbose: bool = False
    ):
        self.skip_empty_cells = skip_empty_cells
        self.preserve_types = preserve_types
        self.verbose = verbose

    def serialize(self, parsed_data: ParsedData) -> str:
        """
        Convert parsed data to YAML string.

        Args:
            parsed_data: Parsed TSV data with metadata

        Returns:
            YAML string representation

        Raises:
            SerializationError: If YAML serialization fails
        """
        try:
            # Create the output structure
            output = {
                "meta": parsed_data.meta,
                "data": self._process_data(parsed_data.data)
            }

            # Convert to YAML with clean formatting
            yaml_output = yaml.dump(
                output,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,  # Reasonable line width
                indent=2
            )

            if self.verbose:
                print(f"Serialized to {len(yaml_output)} characters")

            return yaml_output

        except Exception as e:
            raise SerializationError(f"Failed to serialize to YAML: {e}") from e

    def _process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process data for optimal YAML output.

        Args:
            data: Raw parsed data

        Returns:
            Processed data optimized for YAML serialization
        """
        processed = []

        for item in data:
            if self.skip_empty_cells:
                item = self._remove_empty_values(item)

            if not self.preserve_types:
                item = self._convert_to_strings(item)

            processed.append(item)

        return processed

    def _remove_empty_values(self, obj: Any) -> Any:
        """Recursively remove empty values from nested structures."""
        if isinstance(obj, dict):
            return {
                k: self._remove_empty_values(v)
                for k, v in obj.items()
                if v not in ('', None, [], {})
            }
        elif isinstance(obj, list):
            return [
                self._remove_empty_values(item)
                for item in obj
                if item not in ('', None, [], {})
            ]
        else:
            return obj

    def _convert_to_strings(self, obj: Any) -> Any:
        """Convert all values to strings for consistent YAML output."""
        if isinstance(obj, dict):
            return {k: self._convert_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_strings(item) for item in obj]
        else:
            return str(obj) if obj is not None else ""
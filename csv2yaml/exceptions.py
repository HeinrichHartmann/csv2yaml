"""
Custom exceptions for csv2yaml converter.
"""


class CSV2YAMLError(Exception):
    """Base exception for csv2yaml operations."""
    pass


class ParseError(CSV2YAMLError):
    """Raised when there's an error parsing the input file."""
    pass


class IndexDimensionError(CSV2YAMLError):
    """Raised when index dimensions are invalid for the given data."""
    pass


class SerializationError(CSV2YAMLError):
    """Raised when there's an error serializing to YAML."""
    pass
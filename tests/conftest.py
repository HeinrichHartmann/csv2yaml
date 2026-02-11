"""
Pytest configuration for csv2yaml tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def expected_dir():
    """Fixture providing path to expected output directory."""
    return Path(__file__).parent / "expected"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
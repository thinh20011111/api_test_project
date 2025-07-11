# tests/utils/custom_marks.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "env(name): mark test to run on specific environment"
    )
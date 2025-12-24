# Testing Guide for Daily Temperature Wave

This guide explains how to run and work with the test suite for the Daily Temperature Wave component.

## 🧪 Test Suite Overview

The project includes two types of tests:

### 1. Pytest Tests (Recommended)

These tests don't require Home Assistant and can run in any Python environment:

- **test_pytest_setup.py**: Basic pytest verification (3 tests)
- **test_core_pytest.py**: Core functionality tests (6 tests)
- **Total**: 9 working tests

### 2. Unittest Tests (Legacy)

These tests require Home Assistant to be installed:

- **test_basic.py**: Basic functionality tests
- **test_core.py**: Core functionality tests (unittest version)
- **test_sensor.py**: Sensor functionality tests
- **test_utils.py**: Utility function tests

## 🚀 Running Tests

### Basic Test Execution

```bash
# Run all pytest-compatible tests
python -m pytest tests/test_pytest_setup.py tests/test_core_pytest.py -v

# Run with more verbose output
python -m pytest tests/test_pytest_setup.py tests/test_core_pytest.py -vv

# Run with color output
python -m pytest tests/test_pytest_setup.py tests/test_core_pytest.py -v --color=yes
```

### Test Discovery

Pytest automatically discovers tests using these patterns:
- **Files**: `test_*.py`
- **Functions**: `test_*`
- **Classes**: `Test*`

### Running Specific Tests

```bash
# Run a specific test file
python -m pytest tests/test_core_pytest.py -v

# Run a specific test method
python -m pytest tests/test_core_pytest.py::TestCoreFunctionality::test_parse_temperature_value -v

# Run tests by keyword
python -m pytest -k "temperature" -v
```

## 📊 Test Coverage

### Install Coverage

```bash
pip install pytest-cov
```

### Run Tests with Coverage

```bash
# Basic coverage report
python -m pytest --cov=custom_components --cov-report=term-missing

# HTML coverage report
python -m pytest --cov=custom_components --cov-report=html

# Detailed coverage report
python -m pytest --cov=custom_components --cov-report=term-missing -v
```

### Coverage Configuration

The project includes coverage configuration in `pyproject.toml`:
- **Source**: `custom_components` directory
- **Minimum coverage**: 80% (configurable)
- **Show missing lines**: Enabled

## 🔧 Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --tb=short
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "-v --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

## 📝 Writing Tests

### Test Structure

```python
# Basic test function
def test_something():
    assert 1 + 1 == 2

# Test class
class TestSomething:
    def test_method(self):
        assert True

# Parameterized tests
@pytest.mark.parametrize("input,expected", [(1, 2), (3, 4)])
def test_with_parameters(input, expected):
    assert input + 1 == expected
```

### Assertions

```python
# Basic assertions
assert value == expected
assert value != unexpected
assert value is None
assert value is not None
assert value in container
assert value not in container

# Numerical comparisons
assert value < limit
assert value <= limit
assert value > minimum
assert value >= minimum

# Approximate comparisons
assert abs(value - expected) < tolerance
assert value == pytest.approx(expected)

# Exceptions
with pytest.raises(ExpectedException):
    risky_code()
```

### Fixtures

```python
# Basic fixture
@pytest.fixture
def sample_data():
    return {"key": "value"}

# Using fixtures
def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

## 🧰 Test Utilities

### Mocking

```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    mock = MagicMock()
    mock.return_value = 42
    assert mock() == 42

@patch("module.function")
def test_with_patch(mock_function):
    mock_function.return_value = "mocked"
    assert module.function() == "mocked"
```

### Temporary Files

```python
import tempfile
import os

def test_with_temp_file():
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(b"test data")
        tmp.seek(0)
        assert tmp.read() == b"test data"
```

## 🔍 Debugging Tests

### Verbose Output

```bash
# Show local variables on failure
python -m pytest --tb=long

# Show all local variables
python -m pytest --tb=auto

# Show capture output
python -m pytest -s
```

### Test Selection

```bash
# Run last failed tests first
python -m pytest --ff

# Run failed tests only
python -m pytest --lf

# Stop after first failure
python -m pytest -x
```

## 📦 Test Dependencies

### Install Required Packages

```bash
pip install pytest pytest-cov
```

### Development Setup

```bash
pip install -e .
pip install pytest pytest-cov pytest-mock
```

## 🚨 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'homeassistant'**
- Solution: Run only pytest-compatible tests or install Home Assistant
- Command: `python -m pytest tests/test_pytest_setup.py tests/test_core_pytest.py -v`

**2. Tests not discovered**
- Solution: Check file names start with `test_` and functions start with `test`
- Solution: Verify pytest.ini configuration

**3. Import errors**
- Solution: Check Python path and module structure
- Solution: Ensure proper imports in test files

**4. Slow tests**
- Solution: Use `-n auto` for parallel execution (requires pytest-xdist)
- Solution: Optimize test setup/teardown

## 🎯 Best Practices

### Test Organization

- **Keep tests small and focused**
- **One assertion per test** (when possible)
- **Clear test names** that describe behavior
- **Separate unit and integration tests**

### Test Quality

- **Test edge cases** and boundary conditions
- **Test error conditions** and exceptions
- **Avoid test interdependence**
- **Use fixtures** for common setup

### Test Maintenance

- **Update tests** when code changes
- **Remove obsolete tests**
- **Add tests** for new features
- **Review test coverage** regularly

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Good Practices](https://docs.pytest.org/en/latest/how-to/goodpractices.html)
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/)
- [Real Python pytest Guide](https://realpython.com/pytest-python-testing/)

## 🎉 Test Suite Summary

The Daily Temperature Wave component includes:

- **9 working pytest tests** (no Home Assistant required)
- **Comprehensive coverage** of core functionality
- **Modern testing framework** with pytest
- **Easy to extend** for new features
- **Well documented** test structure

**Happy testing!** 🧪🎉
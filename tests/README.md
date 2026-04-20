# Tests

This directory contains test files for the Product Catalog API.

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── test_api.py          # API endpoint tests
├── test_matcher.py      # ProductMatcher unit tests
└── README.md            # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-cov httpx
```

Or add to `config/requirements.txt`:
```
pytest>=7.4.0
pytest-cov>=4.1.0
httpx>=0.24.0
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestHealthEndpoints

# Run specific test
pytest tests/test_api.py::TestHealthEndpoints::test_health_endpoint

# Run with verbose output
pytest tests/ -v

# Run and stop on first failure
pytest tests/ -x
```

## Test Files

### test_api.py
Tests for API endpoints using FastAPI TestClient:
- Health and system endpoints
- Search endpoints
- Product listing and retrieval
- API documentation

**Example:**
```python
def test_health_endpoint(self):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### test_matcher.py
Unit tests for ProductMatcher core logic:
- Matcher initialization
- Text normalization
- Exact matching
- Fuzzy matching
- Result formatting
- Edge cases

**Example:**
```python
def test_exact_match_found(self, matcher):
    results = matcher.identify_products("IBM Cloud Pak")
    assert len(results) > 0
    assert results[0]["score"] == 1.0
```

## Writing New Tests

### API Endpoint Test Template

```python
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_my_endpoint():
    response = client.get("/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Unit Test Template

```python
import pytest
from src.core.my_module import MyClass

@pytest.fixture
def my_instance():
    return MyClass()

def test_my_function(my_instance):
    result = my_instance.my_method()
    assert result == expected_value
```

## Test Coverage

Generate coverage report:
```bash
pytest tests/ --cov=src --cov-report=html
```

View report:
```bash
# Open htmlcov/index.html in browser
```

## Continuous Integration

Add to CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r config/requirements.txt
    pytest tests/ --cov=src --cov-report=xml
```

## Best Practices

1. **Test Naming**: Use descriptive names starting with `test_`
2. **Fixtures**: Use pytest fixtures for reusable test data
3. **Assertions**: Use clear, specific assertions
4. **Coverage**: Aim for >80% code coverage
5. **Independence**: Tests should not depend on each other
6. **Speed**: Keep tests fast (mock external dependencies)

## Common Issues

### Import Errors
If you get import errors, ensure PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Pytest Not Found
Install pytest:
```bash
pip install pytest
```

### Test Discovery Issues
Ensure:
- Test files start with `test_`
- Test functions start with `test_`
- `__init__.py` exists in test directory

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

# Made with Bob
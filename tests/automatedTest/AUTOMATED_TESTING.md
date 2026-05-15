# Automated Testing Guide

Complete guide for automated testing in the Product Catalog API project.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Coverage Reports](#coverage-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

This project uses a comprehensive automated testing setup with:

- **pytest** for test execution
- **pytest-cov** for coverage reporting
- **GitHub Actions** for CI/CD
- **pre-commit** for automated code quality checks
- **Custom scripts** for easy test execution

### Test Coverage Goals

- **Minimum Coverage**: 70%
- **Target Coverage**: 80%+
- **Critical Paths**: 100%

## Quick Start

### 1. Setup Testing Environment

**Linux/macOS:**
```bash
chmod +x scripts/setup_testing.sh
./scripts/setup_testing.sh
```

**Windows (PowerShell):**
```powershell
# Install dependencies
pip install -r config/requirements.txt

# Install pre-commit
pip install pre-commit
pre-commit install
```

### 2. Run Tests

**Linux/macOS:**
```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage report
./scripts/run_tests.sh --html
```

**Windows (PowerShell):**
```powershell
# Run all tests
.\scripts\run_tests.ps1

# Run with coverage report
.\scripts\run_tests.ps1 -Html
```

**Direct pytest:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── README.md                      # Test documentation
├── test_api.py                    # API endpoint tests
├── test_matcher.py                # Product matcher tests
├── test_confidence_scorer.py      # Confidence scorer tests
└── test_confidence_manual.py      # Manual confidence tests
```

### Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for API endpoints
- `@pytest.mark.smoke` - Quick smoke tests
- `@pytest.mark.slow` - Tests that take longer to run

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestHealthEndpoints

# Run specific test
pytest tests/test_api.py::TestHealthEndpoints::test_health_endpoint
```

### Using Test Scripts

#### Linux/macOS (`run_tests.sh`)

```bash
# Basic usage
./scripts/run_tests.sh

# Verbose output
./scripts/run_tests.sh -v

# Stop on first failure
./scripts/run_tests.sh -x

# Run only unit tests
./scripts/run_tests.sh --unit

# Run only integration tests
./scripts/run_tests.sh --integration

# Run with HTML coverage report
./scripts/run_tests.sh --html

# Run in parallel (4 workers)
./scripts/run_tests.sh -n 4

# Watch mode (rerun on changes)
./scripts/run_tests.sh --watch

# Run tests matching keyword
./scripts/run_tests.sh -k "health"

# Combine options
./scripts/run_tests.sh -v --unit --html
```

#### Windows PowerShell (`run_tests.ps1`)

```powershell
# Basic usage
.\scripts\run_tests.ps1

# Verbose output
.\scripts\run_tests.ps1 -Verbose

# Stop on first failure
.\scripts\run_tests.ps1 -StopOnFail

# Run only unit tests
.\scripts\run_tests.ps1 -Unit

# Run with HTML coverage report
.\scripts\run_tests.ps1 -Html

# Run in parallel (4 workers)
.\scripts\run_tests.ps1 -Parallel 4

# Watch mode
.\scripts\run_tests.ps1 -Watch

# Run tests matching keyword
.\scripts\run_tests.ps1 -Keyword "health"
```

### Advanced Options

```bash
# Run with specific markers
pytest tests/ -m "unit and not slow"

# Run with coverage threshold
pytest tests/ --cov=src --cov-fail-under=80

# Generate multiple report formats
pytest tests/ --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Show slowest tests
pytest tests/ --durations=10

# Run in parallel
pytest tests/ -n auto

# Verbose with traceback
pytest tests/ -vv --tb=long
```

## CI/CD Integration

### GitHub Actions

Automated tests run on:
- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop`
- **Daily schedule** at 2 AM UTC
- **Manual trigger** via workflow_dispatch

#### Workflow Features

1. **Multi-platform Testing**
   - Ubuntu, Windows, macOS
   - Python 3.9, 3.10, 3.11, 3.12

2. **Code Quality Checks**
   - Linting with flake8
   - Type checking with mypy
   - Security scanning with bandit

3. **Coverage Reporting**
   - Automatic upload to Codecov
   - HTML reports as artifacts

4. **Integration Tests**
   - API server startup
   - Health endpoint verification

### Viewing CI Results

1. Go to **Actions** tab in GitHub
2. Select the workflow run
3. View test results and coverage reports
4. Download artifacts for detailed analysis

## Pre-commit Hooks

Pre-commit hooks automatically run before each commit to ensure code quality.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Install commit-msg hook
pre-commit install --hook-type commit-msg
```

### What Gets Checked

1. **File Checks**
   - Trailing whitespace
   - End of file fixer
   - YAML/JSON validation
   - Large file detection

2. **Code Formatting**
   - Black (code formatter)
   - isort (import sorting)

3. **Code Quality**
   - flake8 (linting)
   - mypy (type checking)
   - bandit (security)

4. **Tests**
   - pytest (on commit)
   - pytest with coverage (on push)

### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit
git commit --no-verify -m "message"
```

## Coverage Reports

### Generating Reports

```bash
# Terminal report
pytest tests/ --cov=src --cov-report=term-missing

# HTML report
pytest tests/ --cov=src --cov-report=html

# XML report (for CI)
pytest tests/ --cov=src --cov-report=xml

# JSON report
pytest tests/ --cov=src --cov-report=json
```

### Viewing HTML Reports

```bash
# Generate report
pytest tests/ --cov=src --cov-report=html

# Open in browser
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Coverage Configuration

Coverage settings are in:
- [`pytest.ini`](../pytest.ini) - pytest integration
- [`.coveragerc`](../.coveragerc) - coverage.py settings
- [`pyproject.toml`](../pyproject.toml) - tool configuration

### Understanding Coverage

- **Green lines**: Covered by tests
- **Red lines**: Not covered
- **Yellow lines**: Partially covered (branches)

## Best Practices

### Writing Tests

1. **Use Descriptive Names**
   ```python
   def test_health_endpoint_returns_ok_status():
       # Clear what is being tested
   ```

2. **Follow AAA Pattern**
   ```python
   def test_example():
       # Arrange
       data = setup_test_data()
       
       # Act
       result = function_under_test(data)
       
       # Assert
       assert result == expected_value
   ```

3. **Use Fixtures**
   ```python
   @pytest.fixture
   def sample_data():
       return {"key": "value"}
   
   def test_with_fixture(sample_data):
       assert sample_data["key"] == "value"
   ```

4. **Test Edge Cases**
   - Empty inputs
   - Null values
   - Boundary conditions
   - Error conditions

5. **Keep Tests Independent**
   - No shared state
   - No test order dependencies
   - Clean up after tests

### Test Organization

```python
class TestFeatureName:
    """Group related tests together."""
    
    def test_normal_case(self):
        """Test the happy path."""
        pass
    
    def test_edge_case(self):
        """Test boundary conditions."""
        pass
    
    def test_error_case(self):
        """Test error handling."""
        pass
```

### Performance

1. **Use Markers for Slow Tests**
   ```python
   @pytest.mark.slow
   def test_expensive_operation():
       pass
   ```

2. **Run Fast Tests First**
   ```bash
   pytest tests/ -m "not slow"
   ```

3. **Parallel Execution**
   ```bash
   pytest tests/ -n auto
   ```

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

#### Pytest Not Found

**Problem**: `pytest: command not found`

**Solution**:
```bash
pip install pytest pytest-cov
```

#### Coverage Not Working

**Problem**: Coverage shows 0%

**Solution**:
```bash
# Ensure source path is correct
pytest tests/ --cov=src --cov-report=term

# Check .coveragerc configuration
cat .coveragerc
```

#### Pre-commit Hooks Failing

**Problem**: Hooks fail on commit

**Solution**:
```bash
# Run manually to see errors
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip if needed (not recommended)
git commit --no-verify
```

#### Tests Hanging

**Problem**: Tests don't complete

**Solution**:
```bash
# Run with timeout
pytest tests/ --timeout=30

# Check for infinite loops or blocking operations
pytest tests/ -v --tb=short
```

### Getting Help

1. **Check test output**: `pytest tests/ -v`
2. **Review logs**: Check terminal output
3. **Run single test**: Isolate the problem
4. **Check CI logs**: View GitHub Actions output
5. **Review documentation**: See [tests/README.md](../tests/README.md)

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Continuous Improvement

### Monitoring Test Health

1. **Track Coverage Trends**
   - Monitor coverage over time
   - Set coverage goals
   - Review uncovered code

2. **Review Test Performance**
   - Identify slow tests
   - Optimize where possible
   - Use parallel execution

3. **Update Dependencies**
   - Keep testing tools updated
   - Review security advisories
   - Test with new Python versions

### Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass locally
3. Check coverage meets threshold
4. Run pre-commit hooks
5. Verify CI passes

---

**Made with Bob** 🤖
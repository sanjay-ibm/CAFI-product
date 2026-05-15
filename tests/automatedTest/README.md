# Automated Testing Files

This directory contains all automated testing configuration and scripts for the Product Catalog API.

## 📁 Directory Structure

```
tests/automatedTest/
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       └── test.yml             # CI/CD pipeline configuration
├── scripts/                      # Test automation scripts
│   ├── run_tests.sh             # Linux/macOS test runner
│   ├── run_tests.ps1            # Windows PowerShell test runner
│   └── setup_testing.sh         # Testing environment setup
├── .coveragerc                   # Coverage.py configuration
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── pytest.ini                    # Pytest configuration
├── pyproject.toml               # Project and tool configuration
├── AUTOMATED_TESTING.md         # Complete testing documentation
└── README.md                    # This file
```

## 🚀 Quick Start

### Setup Testing Environment

**Linux/macOS:**
```bash
cd tests/automatedTest
chmod +x scripts/setup_testing.sh
./scripts/setup_testing.sh
```

**Windows:**
```powershell
cd tests\automatedTest
pip install -r ..\..\config\requirements.txt
pip install pre-commit
pre-commit install
```

### Run Tests

**Linux/macOS:**
```bash
# From project root
./tests/automatedTest/scripts/run_tests.sh

# With coverage
./tests/automatedTest/scripts/run_tests.sh --html
```

**Windows:**
```powershell
# From project root
.\tests\automatedTest\scripts\run_tests.ps1

# With coverage
.\tests\automatedTest\scripts\run_tests.ps1 -Html
```

**Direct pytest:**
```bash
# From project root
pytest tests/ --cov=src --cov-report=html
```

## 📋 Configuration Files

### pytest.ini
Pytest configuration including:
- Test discovery patterns
- Coverage settings
- Test markers
- Command line options

### .coveragerc
Coverage.py configuration:
- Source paths
- Omit patterns
- Report settings
- Exclusion rules

### .pre-commit-config.yaml
Pre-commit hooks for:
- Code formatting (Black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- Automated tests

### pyproject.toml
Project configuration for:
- Build system
- Tool settings (Black, isort, mypy, etc.)
- Project metadata

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/test.yml`) runs:

1. **Multi-platform tests** (Ubuntu, Windows, macOS)
2. **Multi-version tests** (Python 3.9-3.12)
3. **Code quality checks** (linting, type checking)
4. **Security scanning** (bandit, safety)
5. **Coverage reporting** (Codecov integration)
6. **Integration tests** (API server validation)

## 📚 Documentation

For complete testing documentation, see:
- [`AUTOMATED_TESTING.md`](AUTOMATED_TESTING.md) - Comprehensive testing guide
- [`../../tests/README.md`](../README.md) - Test structure and examples

## 🛠️ Scripts

### setup_testing.sh
Sets up the complete testing environment:
- Installs dependencies
- Configures pre-commit hooks
- Makes scripts executable
- Runs verification tests

### run_tests.sh / run_tests.ps1
Flexible test runners with options for:
- Verbose/quiet output
- Coverage reporting (HTML, XML, JSON)
- Test filtering (markers, keywords)
- Parallel execution
- Watch mode
- Stop on first failure

## 💡 Usage Examples

```bash
# Run only unit tests
./tests/automatedTest/scripts/run_tests.sh --unit

# Run with verbose output and HTML coverage
./tests/automatedTest/scripts/run_tests.sh -v --html

# Run in watch mode (rerun on changes)
./tests/automatedTest/scripts/run_tests.sh --watch

# Run tests in parallel with 4 workers
./tests/automatedTest/scripts/run_tests.sh -n 4

# Run tests matching keyword
./tests/automatedTest/scripts/run_tests.sh -k "health"
```

## 🔧 Maintenance

### Updating Dependencies

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python packages
pip install --upgrade -r ../../config/requirements.txt
```

### Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Use appropriate markers: `@pytest.mark.unit`, etc.
4. Run tests to verify: `pytest tests/test_new_file.py`

## 📞 Support

For issues or questions:
1. Check [`AUTOMATED_TESTING.md`](AUTOMATED_TESTING.md) troubleshooting section
2. Review test output and logs
3. Check CI/CD pipeline results in GitHub Actions

---

**Made with Bob** 🤖
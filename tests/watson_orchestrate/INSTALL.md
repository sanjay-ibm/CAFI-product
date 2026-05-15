# Installation Guide for Watson Orchestrate Tests

## 🚀 Quick Setup

### Step 1: Install Dependencies

**Option A: Install from local requirements file**
```powershell
cd tests/watson_orchestrate
pip install -r requirements.txt
```

**Option B: Install from project root**
```powershell
pip install -r config/requirements.txt
```

**Option C: Install manually**
```powershell
pip install pytest pytest-html pytest-xdist pytest-cov requests python-dotenv
```

### Step 2: Verify Installation

Check that pytest is installed:
```powershell
pytest --version
```

Expected output:
```
pytest 7.4.0 (or higher)
```

### Step 3: Configure API Key

1. Copy the `.env` file template:
   ```powershell
   # The .env file should already exist, just update it
   ```

2. Get your Watson Orchestrate API key:
   - Visit: https://cio.watson-orchestrate.ibm.com
   - Go to Settings → API Keys
   - Generate or copy your API key

3. Update `.env` file:
   ```bash
   WATSON_ORCHESTRATE_API_KEY=your_actual_api_key_here
   ```

### Step 4: Run Diagnostic Tool

Test your authentication setup:
```powershell
python diagnose_auth.py
```

This will:
- Verify your API key is configured
- Test different authentication methods
- Provide recommendations if authentication fails

### Step 5: Run Tests

**Quick smoke test:**
```powershell
python run_watson_tests.py --quick
```

**Full test suite:**
```powershell
python run_watson_tests.py --all --verbose --html
```

**Check environment:**
```powershell
python run_watson_tests.py --check
```

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError: No module named 'pytest'

**Solution:**
```powershell
pip install pytest
# Or install all requirements
pip install -r requirements.txt
```

### Issue: 401 Unauthorized Error

**Solution:**
```powershell
# Run the diagnostic tool
python diagnose_auth.py

# Follow the recommendations to fix authentication
```

### Issue: Import errors for other modules

**Solution:**
```powershell
# Install all dependencies
pip install -r requirements.txt

# Or install specific missing module
pip install <module-name>
```

## 📦 Dependencies

### Required
- `pytest>=7.4.0` - Testing framework
- `requests>=2.31.0` - HTTP client for API calls
- `python-dotenv>=1.0.0` - Environment variable management

### Optional (for enhanced features)
- `pytest-html>=4.1.0` - HTML test reports
- `pytest-xdist>=3.5.0` - Parallel test execution
- `pytest-cov>=4.1.0` - Code coverage reports

## ✅ Verification Checklist

After installation, verify:

- [ ] pytest is installed: `pytest --version`
- [ ] requests is installed: `python -c "import requests; print(requests.__version__)"`
- [ ] API key is configured: `python run_watson_tests.py --check`
- [ ] Authentication works: `python diagnose_auth.py`
- [ ] Tests can run: `python run_watson_tests.py --quick`

## 🎯 Next Steps

Once installation is complete:

1. Run the quick test to verify everything works
2. Review test results in the `results/` directory
3. Run full test suite with `--all` flag
4. Set up CI/CD integration if needed

## 💡 Tips

- Use a virtual environment to avoid dependency conflicts:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

- Update dependencies regularly:
  ```powershell
  pip install --upgrade -r requirements.txt
  ```

- For development, install additional tools:
  ```powershell
  pip install black flake8 mypy isort
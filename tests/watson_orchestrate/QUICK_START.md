# Quick Start Guide - Watson Orchestrate Tests

## 🚀 Running Tests on Windows

You're in the correct directory: `C:\Users\SANJAYSRIVASTAVA\CAFI-product\tests\watson_orchestrate`

### Option 1: Using Python Directly (Recommended)

```powershell
# Check environment
python run_watson_tests.py --check

# Run quick smoke tests
python run_watson_tests.py --quick

# Run all tests with HTML report
python run_watson_tests.py --all --html --verbose
```

### Option 2: Using PowerShell Script

If you want to use the PowerShell script, you need to:

1. **Check Execution Policy:**
```powershell
Get-ExecutionPolicy
```

2. **If it shows "Restricted", set it to RemoteSigned:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. **Then run with `.\` prefix:**
```powershell
.\run_watson_tests.ps1 -All
```

### Option 3: Direct pytest (Simplest)

```powershell
# Install dependencies first
pip install pytest pytest-html pytest-xdist requests

# Run all tests
pytest test_watson_orchestrate.py -v

# Run with HTML report
pytest test_watson_orchestrate.py --html=results/report.html --self-contained-html -v
```

## 📋 Before Running Tests

### 1. Set up API Key

Create a `.env` file:
```powershell
Copy-Item .env.example .env
notepad .env
```

Add your Watson Orchestrate API key:
```
WATSON_ORCHESTRATE_API_KEY=your_actual_api_key_here
```

### 2. Install Dependencies

```powershell
pip install pytest pytest-html pytest-xdist requests python-dotenv
```

## 🎯 Quick Test Commands

### Check Configuration
```powershell
python run_watson_tests.py --check
```

### Run Quick Smoke Tests (3 questions)
```powershell
python run_watson_tests.py --quick
```

### Run All Tests
```powershell


```

### Run Specific Category
```powershell
python run_watson_tests.py --category product_specific --html
```

### Establish Baseline
```powershell
python run_watson_tests.py --baseline --html
```

### Check for Drift
```powershell
python run_watson_tests.py --drift --html
```

## 📊 View Results

After running tests with `--html` flag:

```powershell
# Open the latest HTML report
start results\report_*.html
```

Or navigate to `results/` folder and open the HTML file.

## ❓ Troubleshooting

### "WATSON_ORCHESTRATE_API_KEY not set"
- Create `.env` file from `.env.example`
- Add your API key

### "pytest not found"
```powershell
pip install pytest pytest-html pytest-xdist requests
```

### "Permission denied" on PowerShell script
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Test a single question
```powershell
pytest test_watson_orchestrate.py::TestResponseQuality::test_product_specific_questions -v
```

## 📝 Example Session

```powershell
# 1. Navigate to test directory
cd C:\Users\SANJAYSRIVASTAVA\CAFI-product\tests\watson_orchestrate

# 2. Check environment
python run_watson_tests.py --check

# 3. Run quick tests
python run_watson_tests.py --quick

# 4. If successful, run full suite
python run_watson_tests.py --all --html --verbose

# 5. View results
start results\report_*.html
```

## 🎓 Next Steps

1. ✅ Run `--check` to verify setup
2. ✅ Run `--quick` for smoke test
3. ✅ Run `--baseline` to establish baseline
4. ✅ Run `--all` for complete test suite
5. ✅ Schedule regular `--drift` monitoring

---

**Need Help?** Check the main [README.md](README.md) for detailed documentation.
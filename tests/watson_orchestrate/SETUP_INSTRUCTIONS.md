# Setup Instructions - Watson Orchestrate Tests

## ✅ Current Status

Your test environment is **almost ready**! You just need to add your API key.

## 🔑 Step 1: Get Your Watson Orchestrate API Key

1. Go to Watson Orchestrate: https://cio.watson-orchestrate.ibm.com
2. Navigate to your account settings or API credentials section
3. Generate or copy your API key

## 📝 Step 2: Add API Key to .env File

You already have the `.env` file open. Add your API key:

```bash
# Watson Orchestrate API Configuration
WATSON_AGENT_ID=6d473302-919e-4204-8c44-5302139947d3
WATSON_ORCHESTRATE_API_KEY=your_actual_api_key_here_replace_this_text
WATSON_ORCHESTRATE_BASE_URL=https://cio.watson-orchestrate.ibm.com/api/v1
```

**Replace** `your_actual_api_key_here_replace_this_text` with your actual API key.

## ✅ Step 3: Verify Setup

After adding your API key, save the `.env` file and run:

```powershell
python run_watson_tests.py --check
```

You should see:
```
✅ WATSON_ORCHESTRATE_API_KEY is set
✅ Test corpus found
✅ pytest is installed
✅ requests library is installed

✅ Environment is properly configured!
```

## 🚀 Step 4: Run Your First Test

Once the check passes, run a quick smoke test:

```powershell
python run_watson_tests.py --quick
```

This will test 3 sample questions to verify everything works.

## 📊 Step 5: Run Full Test Suite

After the quick test succeeds, run the complete test suite:

```powershell
# Run all 150 tests with HTML report
python run_watson_tests.py --all --html --verbose
```

## 🎯 What Happens Next

The tests will:
1. Send questions to your Watson Orchestrate agent
2. Validate response quality (confidence scores, product mentions)
3. Check response times
4. Generate detailed HTML report in `results/` folder

## 📈 Viewing Results

After tests complete:

```powershell
# Open the HTML report
start results\report_*.html
```

Or manually navigate to the `results` folder and open the latest HTML file.

## 🔄 Regular Testing Workflow

### First Time Setup
```powershell
# 1. Establish baseline for drift monitoring
python run_watson_tests.py --baseline --html

# 2. Run full test suite
python run_watson_tests.py --all --html
```

### Daily/Regular Testing
```powershell
# Check for response drift
python run_watson_tests.py --drift --html

# Run specific category
python run_watson_tests.py --category product_specific --html
```

## ❓ Troubleshooting

### Still shows "API key not set" after adding to .env
- Make sure you saved the `.env` file
- Check there are no extra spaces around the `=` sign
- Verify the file is named exactly `.env` (not `.env.txt`)
- Try closing and reopening PowerShell

### "Connection refused" or "Timeout" errors
- Verify your API key is correct
- Check your internet connection
- Verify the Watson Orchestrate service is accessible

### Tests fail with authentication errors
- Your API key may be expired or invalid
- Generate a new API key from Watson Orchestrate
- Update the `.env` file with the new key

## 📞 Need Help?

1. Check [`QUICK_START.md`](QUICK_START.md) for common issues
2. Review [`README.md`](README.md) for detailed documentation
3. Verify your Watson Orchestrate agent is active at:
   https://cio.watson-orchestrate.ibm.com/build/agent/edit/6d473302-919e-4204-8c44-5302139947d3

---

**Next Step:** Add your API key to `.env` file and run `python run_watson_tests.py --check`
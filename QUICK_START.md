# Quick Start Guide - Product Catalog API

## 🚀 How to Run the Project

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

---

## 📦 Step 1: Install Dependencies

```bash
# Navigate to project directory
cd CAFI-product

# Install all required packages
pip install -r config/requirements.txt
```

**What gets installed:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- RapidFuzz - Fuzzy matching
- Pydantic - Data validation
- PyAhoCorasick - Fast string matching
- rank-bm25 - BM25 algorithm
- pytest - Testing framework

---

## ▶️ Step 2: Run the Application

### Option A: Development Mode (Recommended for testing)

```bash
# Run with auto-reload (restarts on code changes)
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Option B: Production Mode

```bash
# Run with multiple workers
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option C: Using Python Module

```bash
# Run directly as Python module
python -m src.api.app
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✓ Matcher initialized
  - Mode: Enhanced
  - Exact aliases: 15234
  - Fuzzy aliases: 15234
  - Aho-Corasick: ✓
  - BM25: ✓
  - N-gram index: 15234 entries
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🌐 Step 3: Access the API

Once running, open your browser:

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Search
```bash
# Search for a product
curl "http://localhost:8000/products/search?query=IBM+Cloud+Pak&limit=5"
```

---

## 🧪 Step 4: Run Tests (Optional)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -f deployment/docker/Dockerfile -t product-catalog-api .

# Run the container
docker run -p 8000:8000 product-catalog-api
```

### Access the API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## ☁️ OpenShift Deployment

### Prerequisites
- OpenShift CLI (`oc`) installed
- Logged into OpenShift cluster

### Deploy to OpenShift

```bash
# 1. Login to OpenShift
oc login https://console-openshift-console.apps.cfai.cp.fyre.ibm.com

# 2. Validate deployment prerequisites
bash deployment/scripts/validate-deployment.sh

# 3. Deploy the application
bash deployment/scripts/deploy.sh
```

### Monitor Deployment

```bash
# Check pod status
oc get pods -n cfai-project

# View logs
oc logs -f deployment/product-catalog-api -n cfai-project

# Get application URL
oc get route product-catalog-api -n cfai-project
```

---

## 📝 Common Commands

### Development

```bash
# Install dependencies
pip install -r config/requirements.txt

# Run with auto-reload
python -m uvicorn src.api.app:app --reload

# Run tests
pytest tests/ -v

# Check code style
black src/ tests/
flake8 src/ tests/
```

### Production

```bash
# Run with multiple workers
python -m uvicorn src.api.app:app --workers 4

# Run with custom port
python -m uvicorn src.api.app:app --port 8080

# Run with logging
python -m uvicorn src.api.app:app --log-level info
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Use enhanced matcher (default: true)
export USE_ENHANCED_MATCHER=true

# Set log level
export LOG_LEVEL=info

# Run the application
python -m uvicorn src.api.app:app
```

### Configuration File

Edit [`deployment/openshift/config/configmap.yaml`](deployment/openshift/config/configmap.yaml) for OpenShift deployments.

---

## 📊 API Endpoints

### Search Products
```bash
GET /products/search?query=IBM+Cloud&limit=10&threshold=0.70
```

### List All Products
```bash
GET /products?limit=100&offset=0
```

### Get Product by Code
```bash
GET /products/5737-H33
```

### Health Check
```bash
GET /health
```

### Statistics
```bash
GET /stats
```

---

## 🐛 Troubleshooting

### Issue: Module not found error

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r config/requirements.txt
```

---

### Issue: Port already in use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Use a different port
python -m uvicorn src.api.app:app --port 8001

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

---

### Issue: Data file not found

**Error:**
```
FileNotFoundError: product_match_dictionary.json not found
```

**Solution:**
```bash
# Ensure you're in the project root directory
cd CAFI-product

# Verify data file exists
ls -la data/product_match_dictionary.json

# Run from project root
python -m uvicorn src.api.app:app --reload
```

---

### Issue: Import errors

**Error:**
```
ImportError: cannot import name 'ProductMatcher'
```

**Solution:**
```bash
# Ensure all __init__.py files exist
ls src/__init__.py
ls src/core/__init__.py
ls src/api/__init__.py

# If missing, they should have been created during setup
```

---

## 📚 Additional Resources

- **[README.md](README.md)** - Full project documentation
- **[PROJECT_STRUCTURE_REVIEW.md](PROJECT_STRUCTURE_REVIEW.md)** - Structure analysis
- **[docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)** - Deployment guide
- **[docs/troubleshooting/TROUBLESHOOTING.md](docs/troubleshooting/TROUBLESHOOTING.md)** - Troubleshooting guide
- **[tests/README.md](tests/README.md)** - Testing documentation

---

## ✅ Verification Checklist

After running the project, verify:

- [ ] Application starts without errors
- [ ] Health endpoint returns 200 OK: http://localhost:8000/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Search endpoint works: `/products/search?query=IBM`
- [ ] Tests pass: `pytest tests/ -v`

---

## 🎯 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run Tests**: `pytest tests/ -v`
3. **Try Searches**: Test different product queries
4. **Deploy**: Follow OpenShift deployment guide
5. **Customize**: Modify configuration as needed

---

## 💡 Tips

- Use `--reload` flag during development for auto-restart
- Check logs if application doesn't start
- Ensure you're in the project root directory
- Use virtual environment for isolated dependencies
- Run tests before deploying to production

---

# Correct Commands to Run the Project

## ❌ Your Command (Has Typo)
```bash
uvicorn src.api.app:app --host app:app0.0.0.0 --port 8010 --reload
#                              ^^^^^^^^^^^^^^ WRONG - This is the typo!
```

## ✅ Correct Commands

### Option 1: Run on localhost (Recommended for Windows)
```bash
uvicorn src.api.app:app --host 127.0.0.1 --port 8010 --reload
```

### Option 2: Run on all interfaces
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8010 --reload
```

### Option 3: Default host (localhost)
```bash
uvicorn src.api.app:app --port 8010 --reload
```

### Option 4: Using Python module (Simplest)
```bash
python -m uvicorn src.api.app:app --reload
```

---

## 🔍 Understanding the Error

**Error Message:**
```
ERROR: [Errno 11001] getaddrinfo failed
```

**Cause:** The `--host` parameter received `app:app0.0.0.0` instead of `0.0.0.0`

**What happened:**
- You typed: `--host app:app0.0.0.0`
- Should be: `--host 0.0.0.0`
- The system tried to resolve `app:app0.0.0.0` as a hostname and failed

---

## 📋 Step-by-Step Instructions

### Step 1: Open Terminal/PowerShell
```powershell
# Navigate to project directory
cd C:\Users\SANJAYSRIVASTAVA\CAFI-product
```

### Step 2: Run the Application
```powershell
# Recommended for Windows
uvicorn src.api.app:app --host 127.0.0.1 --port 8010 --reload
```

### Step 3: Verify It's Running
You should see:
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\SANJAYSRIVASTAVA\\CAFI-product']
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
✓ Matcher initialized
  - Mode: Enhanced
  - Exact aliases: 15234
  - Fuzzy aliases: 15234
INFO:     Application startup complete.
```

### Step 4: Access the API
Open your browser:
- **API Docs**: http://127.0.0.1:8010/docs
- **Health Check**: http://127.0.0.1:8010/health

-------------------------------------------------------------------

## 🎯 Quick Reference

### Windows PowerShell Commands

```powershell
# Install dependencies
pip install -r config/requirements.txt

# Run on localhost (safest for Windows)
uvicorn src.api.app:app --host 127.0.0.1 --port 8010 --reload

# Run on default port 8000
uvicorn src.api.app:app --reload

# Run with Python module
python -m uvicorn src.api.app:app --reload
```

### Test the API

```powershell
# Using curl (if installed)
curl http://127.0.0.1:8010/health

# Using PowerShell
Invoke-WebRequest -Uri http://127.0.0.1:8010/health

# Or just open in browser
start http://127.0.0.1:8010/docs
```

---

## 🐛 Common Issues on Windows

### Issue 1: Port Already in Use
```
ERROR: [Errno 10048] Only one usage of each socket address
```

**Solution:**
```powershell
# Use a different port
uvicorn src.api.app:app --host 127.0.0.1 --port 8011 --reload

# Or find and kill the process
netstat -ano | findstr :8010
taskkill /PID <process_id> /F
```

### Issue 2: Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Reinstall dependencies
pip install -r config/requirements.txt
```

### Issue 3: Permission Denied
```
PermissionError: [WinError 5] Access is denied
```

**Solution:**
```powershell
# Run PowerShell as Administrator
# Or use a port > 1024
uvicorn src.api.app:app --host 127.0.0.1 --port 8010 --reload
```

---

## ✅ Verification Steps

After running the command, verify:

1. **No errors in terminal** ✓
2. **See "Application startup complete"** ✓
3. **Open http://127.0.0.1:8010/docs** ✓
4. **Try a search query** ✓

---

## 💡 Pro Tips

1. **Use 127.0.0.1 on Windows** instead of 0.0.0.0 (more reliable)


**Made with Bob** 🤖
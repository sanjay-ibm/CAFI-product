# Watson Orchestrate Agent Automation Tests

Comprehensive automation test suite for the **CFAI_Testing_Product_Support** Watson Orchestrate agent focusing on response quality and drift monitoring.

**Agent URL:** https://cio.watson-orchestrate.ibm.com/build/agent/edit/6d473302-919e-4204-8c44-5302139947d3

## 📋 Table of Contents

- [Overview](#overview)
- [Test Coverage](#test-coverage)
- [Quick Start](#quick-start)
- [Test Data Corpus](#test-data-corpus)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Configuration](#configuration)
- [Drift Monitoring](#drift-monitoring)
- [Reporting](#reporting)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This test suite provides comprehensive automation testing for the Watson Orchestrate agent with:

- **150+ Test Questions** across 5 categories
- **Response Quality Validation** with confidence scoring
- **Drift Monitoring** to detect response changes over time
- **Multi-turn Conversation Testing** for context retention
- **Performance Metrics** tracking
- **Automated Reporting** with HTML and JSON outputs

### Test Architecture

```
tests/watson_orchestrate/
├── test_watson_orchestrate.py    # Main test suite
├── test_data_corpus.json          # 50 core test questions
├── extended_test_corpus.json      # 100 additional questions
├── conftest.py                    # Pytest fixtures and configuration
├── test_config.json               # Test configuration
├── run_watson_tests.py            # Python test runner
├── run_watson_tests.sh            # Linux/macOS runner
├── run_watson_tests.ps1           # Windows PowerShell runner
├── .env.example                   # Environment template
├── baseline/                      # Baseline responses
├── results/                       # Test results and reports
└── README.md                      # This file
```

## 📊 Test Coverage

### Test Question Categories (150 Total)

1. **Product Specific Questions (40)** - Configuration, features, technical specs
   - Envizi, Cloud Pak, Watson, Maximo, Security products
   - Storage, Middleware, Database, Automation, Blockchain
   - AI/ML, IoT, Supply Chain, Sustainability, Mainframe

2. **General IBM Questions (20)** - Support, licensing, training, documentation
   - Support hours and ticket management
   - Licensing models and renewals
   - Training resources and certifications
   - Partner programs and compliance

3. **Multi-turn Conversations (12)** - Context retention across messages
   - Product inquiries with follow-ups
   - Troubleshooting scenarios
   - Configuration assistance
   - Product selection guidance

4. **Product Comparison (12)** - Comparative analysis
   - Cloud Pak variants
   - Watson services
   - Security solutions
   - Storage and monitoring tools

5. **Troubleshooting Scenarios (16)** - Problem resolution
   - Installation issues
   - Performance problems
   - Connectivity errors
   - Authentication failures

### Quality Metrics Tracked

- **Confidence Scores** - Agent's confidence in responses
- **Response Quality Score** - Composite quality metric (0-1)
- **Product Mention Accuracy** - Correct product references
- **Response Completeness** - Adequate detail level
- **Response Time** - Performance metrics
- **Context Retention** - Multi-turn conversation quality

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install pytest pytest-html pytest-xdist requests python-dotenv
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Watson Orchestrate API key
# WATSON_ORCHESTRATE_API_KEY=your_api_key_here
```

### 3. Run Tests

**Linux/macOS:**
```bash
# Make script executable
chmod +x run_watson_tests.sh

# Run all tests
./run_watson_tests.sh --all

# Run quick smoke tests
./run_watson_tests.sh --quick
```

**Windows PowerShell:**
```powershell
# Run all tests
.\run_watson_tests.ps1 -All

# Run quick smoke tests
.\run_watson_tests.ps1 -Quick
```

**Python Direct:**
```bash
# Run all tests
python run_watson_tests.py --all

# Run with HTML report
python run_watson_tests.py --all --html --verbose
```

## 📚 Test Data Corpus

### Primary Corpus (`test_data_corpus.json`)

50 carefully curated questions covering core scenarios:

```json
{
  "id": "PS001",
  "category": "product_specific",
  "question": "How do I configure Envizi for ESG reporting?",
  "expected_response_type": "configuration_guide",
  "expected_products": ["Envizi"],
  "confidence_threshold": 0.8,
  "tags": ["configuration", "esg", "reporting"]
}
```

### Extended Corpus (`extended_test_corpus.json`)

100 additional questions for comprehensive coverage across:
- Advanced product features
- Edge cases and error scenarios
- Integration and deployment questions
- Performance and optimization queries

## 🧪 Running Tests

### Test Execution Modes

#### 1. All Tests
```bash
# Run complete test suite
python run_watson_tests.py --all --html --verbose
```

#### 2. Baseline Establishment
```bash
# Establish baseline responses for drift monitoring
python run_watson_tests.py --baseline --html
```

#### 3. Drift Monitoring
```bash
# Check for response drift against baseline
python run_watson_tests.py --drift --html
```

#### 4. Performance Tests
```bash
# Run performance-focused tests
python run_watson_tests.py --performance --verbose
```

#### 5. Category-Specific Tests
```bash
# Test specific category
python run_watson_tests.py --category product_specific --html

# Available categories:
# - product_specific
# - general_ibm
# - multi_turn
# - product_comparison
# - troubleshooting
```

#### 6. Quick Smoke Tests
```bash
# Run fast validation tests
python run_watson_tests.py --quick
```

### Advanced Options

```bash
# Run with parallel execution
python run_watson_tests.py --all --parallel --workers 4

# Run with coverage report
python run_watson_tests.py --all --coverage

# Check environment configuration
python run_watson_tests.py --check

# Generate summary from latest results
python run_watson_tests.py --summary
```

## 📁 Test Categories

### 1. Response Quality Tests

**Class:** `TestResponseQuality`

Validates:
- Response structure completeness
- Confidence score thresholds
- Product mention accuracy
- Overall quality scoring

```python
@pytest.mark.parametrize("test_case", test_corpus)
def test_product_specific_questions(watson_client, test_case, response_validator):
    response = watson_client.send_message(test_case["question"])
    assert response_validator.validate_confidence_score(response, 0.8)
```

### 2. Multi-turn Conversation Tests

**Class:** `TestMultiTurnConversations`

Validates:
- Context retention across turns
- Follow-up question handling
- Conversation coherence

```python
def test_multi_turn_context_retention(watson_client, test_case):
    conversation_id = watson_client.create_conversation()
    response1 = watson_client.send_message(test_case["question"], conversation_id)
    response2 = watson_client.send_message(test_case["follow_up"], conversation_id)
    # Validate context maintained
```

### 3. Product Comparison Tests

**Class:** `TestProductComparison`

Validates:
- All products mentioned
- Comparative analysis provided
- Recommendation quality

### 4. Troubleshooting Tests

**Class:** `TestTroubleshooting`

Validates:
- Actionable guidance provided
- Step-by-step instructions
- Problem resolution approach

### 5. Drift Monitoring Tests

**Class:** `TestDriftMonitoring`

Validates:
- Response consistency over time
- Confidence score stability
- Content drift detection

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Required
WATSON_AGENT_ID=6d473302-919e-4204-8c44-5302139947d3
WATSON_ORCHESTRATE_API_KEY=your_api_key_here

# Optional
WATSON_ORCHESTRATE_BASE_URL=https://cio.watson-orchestrate.ibm.com/api/v1
WATSON_TIMEOUT=30
CONFIDENCE_THRESHOLD=0.7
DRIFT_THRESHOLD=0.15
MAX_RETRIES=3
RETRY_DELAY=2
```

### Test Configuration (`test_config.json`)

```json
{
  "quality_thresholds": {
    "product_specific": {
      "min_confidence": 0.8,
      "min_quality_score": 0.7,
      "max_response_time_ms": 5000
    }
  },
  "drift_monitoring": {
    "enabled": true,
    "drift_alert_threshold": 0.15
  }
}
```

## 📈 Drift Monitoring

### How It Works

1. **Baseline Establishment**
   ```bash
   python run_watson_tests.py --baseline
   ```
   - Runs test corpus and saves responses
   - Creates `baseline/baseline_responses.json`

2. **Drift Detection**
   ```bash
   python run_watson_tests.py --drift
   ```
   - Compares current responses to baseline
   - Calculates drift metrics:
     - Confidence drift (60% weight)
     - Response length drift (40% weight)
   - Alerts if drift > 15% threshold

3. **Drift Metrics**
   ```python
   {
     "drift_detected": true,
     "drift_metrics": {
       "confidence_drift": 0.12,
       "response_length_drift": 0.08,
       "overall_drift": 0.104
     },
     "recommendation": "Investigate response changes"
   }
   ```

### Interpreting Drift

- **< 10% drift** - Normal variation
- **10-15% drift** - Monitor closely
- **> 15% drift** - Investigation recommended
- **> 25% drift** - Significant change detected

## 📊 Reporting

### HTML Reports

Generated with `--html` flag:
```bash
python run_watson_tests.py --all --html
```

Location: `results/report_YYYYMMDD_HHMMSS.html`

Features:
- Test pass/fail summary
- Detailed test results
- Performance metrics
- Failure analysis

### JSON Reports

Automatically generated: `results/test_results_YYYYMMDD_HHMMSS.json`

```json
{
  "test_id": "PS001",
  "status": "passed",
  "confidence": 0.85,
  "quality_score": 0.78,
  "response_time_ms": 1234,
  "timestamp": "2026-05-14T10:30:00Z"
}
```

### Summary Reports

```bash
python run_watson_tests.py --summary
```

Displays:
- Total tests run
- Pass/fail rates
- Average confidence scores
- Performance statistics

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Watson Orchestrate Tests

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-html pytest-xdist requests
      
      - name: Run Watson Orchestrate Tests
        env:
          WATSON_ORCHESTRATE_API_KEY: ${{ secrets.WATSON_API_KEY }}
        run: |
          cd tests/watson_orchestrate
          python run_watson_tests.py --all --html
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: tests/watson_orchestrate/results/
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    triggers {
        cron('H 0 * * *')  // Daily
    }
    
    environment {
        WATSON_ORCHESTRATE_API_KEY = credentials('watson-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install pytest pytest-html pytest-xdist requests'
            }
        }
        
        stage('Test') {
            steps {
                dir('tests/watson_orchestrate') {
                    sh 'python run_watson_tests.py --all --html'
                }
            }
        }
        
        stage('Report') {
            steps {
                publishHTML([
                    reportDir: 'tests/watson_orchestrate/results',
                    reportFiles: 'report_*.html',
                    reportName: 'Watson Orchestrate Test Report'
                ])
            }
        }
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Not Set
```
Error: WATSON_ORCHESTRATE_API_KEY not set
```

**Solution:**
```bash
# Create .env file
cp .env.example .env
# Edit .env and add your API key
```

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'pytest'
```

**Solution:**
```bash
pip install pytest pytest-html pytest-xdist requests
```

#### 3. Connection Timeout
```
requests.exceptions.Timeout: Request timed out
```

**Solution:**
```bash
# Increase timeout in .env
WATSON_TIMEOUT=60
```

#### 4. Baseline Not Found
```
Warning: No baseline available
```

**Solution:**
```bash
# Establish baseline first
python run_watson_tests.py --baseline
```

### Debug Mode

```bash
# Run with maximum verbosity
python run_watson_tests.py --all --verbose -vv

# Run single test for debugging
pytest tests/watson_orchestrate/test_watson_orchestrate.py::TestResponseQuality::test_product_specific_questions[PS001] -vv
```

### Logs

Test execution logs are saved in:
- `results/test_results_*.json` - Detailed results
- `results/report_*.html` - HTML reports
- Console output - Real-time progress

## 📞 Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review test configuration in `test_config.json`
3. Verify environment variables in `.env`
4. Check Watson Orchestrate agent status
5. Review test logs in `results/` directory

## 🎓 Best Practices

1. **Run Baseline First**
   - Establish baseline before drift monitoring
   - Update baseline after agent changes

2. **Regular Testing**
   - Schedule daily automated runs
   - Monitor drift trends over time

3. **Test Maintenance**
   - Update test corpus as products evolve
   - Review and adjust confidence thresholds
   - Keep expected responses current

4. **Performance Monitoring**
   - Track response times
   - Set appropriate timeout values
   - Monitor API rate limits

5. **Result Analysis**
   - Review failed tests promptly
   - Investigate significant drift
   - Update baselines when appropriate

## 📝 Test Metrics Summary

| Metric | Target | Critical |
|--------|--------|----------|
| Confidence Score | ≥ 0.7 | ≥ 0.6 |
| Quality Score | ≥ 0.7 | ≥ 0.6 |
| Response Time | < 5s | < 10s |
| Drift Threshold | < 15% | < 25% |
| Pass Rate | ≥ 90% | ≥ 80% |

---

**Created:** 2026-05-14  
**Version:** 1.0.0  
**Agent:** CFAI_Testing_Product_Support  
**Made with Bob** 🤖
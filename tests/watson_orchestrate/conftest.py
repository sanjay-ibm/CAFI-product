"""
Pytest configuration and fixtures for Watson Orchestrate tests.
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any, List


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "watson_orchestrate: mark test as Watson Orchestrate integration test"
    )
    config.addinivalue_line(
        "markers", "drift_monitoring: mark test as drift monitoring test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "multi_turn: mark test as multi-turn conversation test"
    )
    config.addinivalue_line(
        "markers", "baseline: mark test as baseline establishment test"
    )


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    Load test configuration from environment and config file.
    
    Returns:
        Dictionary with test configuration
    """
    config = {
        "agent_id": os.getenv("WATSON_AGENT_ID", "6d473302-919e-4204-8c44-5302139947d3"),
        "api_key": os.getenv("WATSON_ORCHESTRATE_API_KEY", ""),
        "base_url": os.getenv(
            "WATSON_ORCHESTRATE_BASE_URL",
            "https://cio.watson-orchestrate.ibm.com/api/v1"
        ),
        "timeout": int(os.getenv("WATSON_TIMEOUT", "30")),
        "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.7")),
        "drift_threshold": float(os.getenv("DRIFT_THRESHOLD", "0.15")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "2")),
    }
    
    # Load from config file if exists
    config_file = Path(__file__).parent / "test_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            file_config = json.load(f)
            config.update(file_config)
    
    return config


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get test data directory path."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def results_dir(test_data_dir) -> Path:
    """Get or create results directory."""
    results = test_data_dir / "results"
    results.mkdir(exist_ok=True)
    return results


@pytest.fixture(scope="session")
def baseline_dir(test_data_dir) -> Path:
    """Get or create baseline directory."""
    baseline = test_data_dir / "baseline"
    baseline.mkdir(exist_ok=True)
    return baseline


@pytest.fixture(scope="function")
def test_result_logger(results_dir):
    """
    Fixture to log test results to file.
    
    Usage in test:
        def test_example(test_result_logger):
            test_result_logger.log({
                "test_id": "PS001",
                "status": "passed",
                "metrics": {...}
            })
    """
    from datetime import datetime
    
    class TestResultLogger:
        def __init__(self, results_dir: Path):
            self.results_dir = results_dir
            self.results = []
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        def log(self, result: Dict[str, Any]):
            """Log a test result."""
            result["timestamp"] = datetime.now().isoformat()
            self.results.append(result)
        
        def save(self):
            """Save all logged results to file."""
            if self.results:
                output_file = self.results_dir / f"test_results_{self.timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2)
    
    logger = TestResultLogger(results_dir)
    yield logger
    logger.save()


@pytest.fixture(scope="session")
def sample_questions() -> List[Dict[str, Any]]:
    """
    Provide sample questions for quick testing.
    
    Returns:
        List of sample test questions
    """
    return [
        {
            "id": "SAMPLE_001",
            "category": "product_specific",
            "question": "How do I configure Envizi for ESG reporting?",
            "expected_products": ["Envizi"],
            "confidence_threshold": 0.8
        },
        {
            "id": "SAMPLE_002",
            "category": "general_ibm",
            "question": "What are IBM support hours?",
            "expected_products": [],
            "confidence_threshold": 0.7
        },
        {
            "id": "SAMPLE_003",
            "category": "product_comparison",
            "question": "What's the difference between Cloud Pak for Data and Cloud Pak for Integration?",
            "expected_products": ["IBM Cloud Pak for Data", "IBM Cloud Pak for Integration"],
            "confidence_threshold": 0.8
        }
    ]


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers and skip conditions.
    """
    # Skip tests if API key not configured
    skip_no_api_key = pytest.mark.skip(reason="WATSON_ORCHESTRATE_API_KEY not set")
    
    for item in items:
        if "watson_orchestrate" in item.keywords:
            if not os.getenv("WATSON_ORCHESTRATE_API_KEY"):
                item.add_marker(skip_no_api_key)


def pytest_html_report_title(report):
    """Customize HTML report title."""
    report.title = "Watson Orchestrate Agent Test Report"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results for custom reporting.
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Add custom attributes to test report
    if rep.when == "call":
        setattr(item, f"rep_{rep.when}", rep)

# Made with Bob

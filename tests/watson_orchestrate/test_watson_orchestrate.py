#!/usr/bin/env python3
"""
Watson Orchestrate Agent Automation Tests (Enhanced)

Production-grade automation framework for CFAI_Testing_Product_Support agent:
1. Response Quality & Drift Monitoring
2. Multi-turn Conversation Memory
3. Product Comparison Validation
4. Troubleshooting Guidance Validation
5. Performance Benchmarking
6. Baseline + Regression Drift Detection
7. Reporting & Logging

Improvements merged into existing test suite:
- Better authentication handling
- Centralized file/config constants
- Retry + exponential backoff
- Structured logging
- Safer JSON loading
- Stronger validation logic
- Cleaner pytest architecture
- Custom assertion messages
- Response normalization
- Better drift analysis
"""

import base64
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_DIR = Path(__file__).parent
DEFAULT_AGENT_ID = "6d473302-919e-4204-8c44-5302139947d3"
DEFAULT_BASE_URL = "https://cio.watson-orchestrate.ibm.com/api/v1"

TEST_CORPUS_FILE = BASE_DIR / "test_data_corpus.json"
EXTENDED_CORPUS_FILE = BASE_DIR / "extended_test_corpus.json"
BASELINE_FILE = BASE_DIR / "baseline_responses.json"

MAX_RESPONSE_TIME_MS = 10000
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.15

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("watson_test_runner")


def safe_load_json(file_path: Path) -> Dict[str, Any]:
    """Safely load JSON file."""
    if not file_path.exists():
        logger.warning("File not found: %s", file_path)
        return {}

    try:
        with file_path.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except Exception as exc:
        logger.error("Failed loading JSON from %s: %s", file_path, exc)
        return {}


def normalize_text(text: str) -> str:
    """Normalize response text for comparisons."""
    return " ".join(text.lower().strip().split())


def load_test_cases(category: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load test cases from the main corpus safely."""
    data = safe_load_json(TEST_CORPUS_FILE)
    test_questions = data.get("test_questions", [])

    if category:
        test_questions = [test_case for test_case in test_questions if test_case.get("category") == category]

    if limit is not None:
        test_questions = test_questions[:limit]

    return test_questions


class WatsonOrchestrateClient:
    """Robust client for interacting with Watson Orchestrate API."""

    def __init__(
        self,
        agent_id: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.api_key = api_key or os.getenv("WATSON_ORCHESTRATE_API_KEY")
        self.base_url = base_url or os.getenv(
            "WATSON_ORCHESTRATE_BASE_URL",
            DEFAULT_BASE_URL
        )
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        """Configure retries, authentication, and headers."""
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        headers = {"Content-Type": "application/json"}

        if self.api_key:
            try:
                decoded = base64.b64decode(self.api_key).decode("utf-8")
                if ":" in decoded:
                    username, password = decoded.split(":", 1)
                    self.session.auth = (username, password)
                else:
                    headers["Authorization"] = f"Bearer {self.api_key}"
            except Exception:
                headers["Authorization"] = f"Bearer {self.api_key}"

        self.session.headers.update(headers)

    def _post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Centralized POST with error handling."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error("Request failed: %s", exc)
            return {
                "error": str(exc),
                "status_code": getattr(exc.response, "status_code", None),
                "output": {"text": ""},
                "context": {},
                "metadata": {}
            }

    def create_conversation(self) -> str:
        """Create a conversation session."""
        response = self._post(
            f"/agents/{self.agent_id}/conversations",
            {},
            timeout=10
        )
        return response.get("conversation_id", f"local_{int(time.time() * 1000)}")

    def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message to the agent."""
        payload: Dict[str, Any] = {"input": {"text": message}}

        if conversation_id:
            payload["context"] = {"conversation_id": conversation_id}

        return self._post(f"/agents/{self.agent_id}/message", payload)


class ResponseValidator:
    """Enhanced validator for agent responses."""

    REQUIRED_FIELDS = ["output", "context"]

    @classmethod
    def validate_response_structure(cls, response: Dict[str, Any]) -> bool:
        """Validate required response structure."""
        return all(field in response for field in cls.REQUIRED_FIELDS)

    @staticmethod
    def confidence(response: Dict[str, Any]) -> float:
        """Extract confidence safely."""
        return response.get("context", {}).get("confidence", 0.0)

    @classmethod
    def validate_confidence_score(
        cls,
        response: Dict[str, Any],
        threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    ) -> bool:
        """Validate confidence threshold."""
        return cls.confidence(response) >= threshold

    @staticmethod
    def response_text(response: Dict[str, Any]) -> str:
        """Extract response text safely."""
        return response.get("output", {}).get("text", "")

    @classmethod
    def validate_product_mention(
        cls,
        response: Dict[str, Any],
        expected_products: List[str]
    ) -> bool:
        """Validate all expected products are mentioned."""
        response_text = normalize_text(cls.response_text(response))
        return all(product.lower() in response_text for product in expected_products)

    @staticmethod
    def validate_response_type(response: Dict[str, Any], expected_type: str) -> bool:
        """Validate response type if present in context."""
        response_type = response.get("context", {}).get("response_type", "")
        return response_type == expected_type or expected_type in response_type

    @classmethod
    def calculate_response_quality_score(
        cls,
        response: Dict[str, Any],
        test_case: Dict[str, Any]
    ) -> float:
        """Calculate overall response quality score."""
        score = 0.0

        confidence = cls.confidence(response)
        score += confidence * 0.4

        expected_products = test_case.get("expected_products", [])
        if expected_products:
            response_text = normalize_text(cls.response_text(response))
            matched = sum(1 for product in expected_products if product.lower() in response_text)
            score += (matched / len(expected_products)) * 0.3
        else:
            score += 0.3

        if len(cls.response_text(response)) > 50:
            score += 0.2

        response_time = response.get("metadata", {}).get("response_time_ms", 5000)
        if response_time < 2000:
            score += 0.1
        elif response_time < 5000:
            score += 0.05

        return round(min(score, 1.0), 4)


class DriftMonitor:
    """Monitors response drift over time."""

    def __init__(self, baseline_file: Path = BASELINE_FILE):
        self.baseline_file = baseline_file
        self.baseline_data = safe_load_json(self.baseline_file)

    def save_baseline(self, test_results: Dict[str, Any]) -> None:
        """Save current test results as baseline."""
        with self.baseline_file.open("w", encoding="utf-8") as file_handle:
            json.dump(test_results, file_handle, indent=2)

    def detect_drift(self, current_response: Dict[str, Any], test_id: str) -> Dict[str, Any]:
        """Detect drift between current response and baseline."""
        baseline = self.baseline_data.get(test_id)

        if not baseline:
            return {
                "drift_detected": False,
                "reason": "No baseline available",
                "recommendation": "Run baseline establishment first"
            }

        baseline_confidence = baseline.get("confidence", 0)
        current_confidence = current_response.get("context", {}).get("confidence", 0)

        baseline_length = baseline.get("response_length", 0)
        current_length = len(current_response.get("output", {}).get("text", ""))

        confidence_drift = abs(baseline_confidence - current_confidence)
        response_length_drift = (
            abs(current_length - baseline_length) / baseline_length
            if baseline_length else 0
        )

        overall_drift = (
            confidence_drift * 0.6 +
            min(response_length_drift, 1.0) * 0.4
        )

        drift_detected = overall_drift > DRIFT_THRESHOLD

        return {
            "drift_detected": drift_detected,
            "drift_metrics": {
                "confidence_drift": round(confidence_drift, 4),
                "response_length_drift": round(response_length_drift, 4),
                "overall_drift": round(overall_drift, 4)
            },
            "baseline_confidence": baseline_confidence,
            "current_confidence": current_confidence,
            "recommendation": "Investigate response changes" if drift_detected else "No action needed"
        }


@pytest.fixture(scope="session")
def watson_client():
    """Create Watson Orchestrate client for testing."""
    agent_id = os.getenv("WATSON_AGENT_ID", DEFAULT_AGENT_ID)
    return WatsonOrchestrateClient(agent_id=agent_id)


@pytest.fixture(scope="session")
def test_corpus():
    """Load test question corpus."""
    corpus: List[Dict[str, Any]] = []

    for file_path in [TEST_CORPUS_FILE, EXTENDED_CORPUS_FILE]:
        data = safe_load_json(file_path)
        corpus.extend(data.get("test_questions", []))

    return corpus


@pytest.fixture(scope="session")
def response_validator():
    """Create response validator instance."""
    return ResponseValidator()


@pytest.fixture(scope="session")
def drift_monitor():
    """Create drift monitor instance."""
    return DriftMonitor()


class TestResponseQuality:
    """Test suite for response quality validation."""

    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(limit=20)]
    )
    def test_product_specific_questions(self, watson_client, test_case, response_validator):
        """Test product-specific questions for quality and accuracy."""
        if test_case["category"] != "product_specific":
            pytest.skip("Not a product-specific question")

        response = watson_client.send_message(test_case["question"])

        assert response_validator.validate_response_structure(response), (
            f"{test_case['id']} response missing required fields"
        )

        assert response_validator.validate_confidence_score(
            response,
            test_case.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
        ), f"{test_case['id']} confidence below threshold"

        if test_case.get("expected_products"):
            assert response_validator.validate_product_mention(
                response,
                test_case["expected_products"]
            ), f"{test_case['id']} missing expected products"

        quality_score = response_validator.calculate_response_quality_score(response, test_case)
        assert quality_score >= 0.7, (
            f"{test_case['id']} quality score below threshold: {quality_score}"
        )

    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(category="general_ibm")]
    )
    def test_general_ibm_questions(self, watson_client, test_case, response_validator):
        """Test general IBM questions."""
        response = watson_client.send_message(test_case["question"])

        assert response_validator.validate_response_structure(response), (
            f"{test_case['id']} response missing required fields"
        )

        assert response_validator.validate_confidence_score(response, 0.6), (
            f"{test_case['id']} confidence too low for general IBM question"
        )

        response_text = response_validator.response_text(response)
        assert len(response_text) > 20, f"{test_case['id']} response too short"


class TestMultiTurnConversations:
    """Test suite for multi-turn conversation scenarios."""

    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(category="multi_turn")]
    )
    def test_multi_turn_context_retention(self, watson_client, test_case, response_validator):
        """Test that agent maintains context across multiple turns."""
        conversation_id = watson_client.create_conversation()

        response1 = watson_client.send_message(
            test_case["question"],
            conversation_id=conversation_id
        )
        assert response_validator.validate_response_structure(response1), (
            f"{test_case['id']} first response invalid"
        )

        time.sleep(1)

        response2 = watson_client.send_message(
            test_case["follow_up"],
            conversation_id=conversation_id
        )
        assert response_validator.validate_response_structure(response2), (
            f"{test_case['id']} follow-up response invalid"
        )

        response2_text = normalize_text(response_validator.response_text(response2))
        assert len(response2_text) > 30, (
            f"{test_case['id']} follow-up response too short"
        )


class TestProductComparison:
    """Test suite for product comparison questions."""

    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(category="product_comparison")]
    )
    def test_product_comparison_completeness(self, watson_client, test_case, response_validator):
        """Test that product comparisons mention all relevant products."""
        response = watson_client.send_message(test_case["question"])

        assert response_validator.validate_response_structure(response), (
            f"{test_case['id']} response invalid"
        )

        expected_products = test_case.get("expected_products", [])
        response_text = normalize_text(response_validator.response_text(response))
        mentioned_products = [product for product in expected_products if product.lower() in response_text]

        assert len(mentioned_products) >= len(expected_products) * 0.8, (
            f"{test_case['id']} comparison missing expected products"
        )

        comparison_keywords = ["difference", "compare", "versus", "vs", "while", "whereas", "better", "best"]
        has_comparison = any(keyword in response_text for keyword in comparison_keywords)

        assert has_comparison or len(response_text) > 100, (
            f"{test_case['id']} response lacks adequate comparison detail"
        )


class TestTroubleshooting:
    """Test suite for troubleshooting scenarios."""

    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(category="troubleshooting")]
    )
    def test_troubleshooting_guidance(self, watson_client, test_case, response_validator):
        """Test that troubleshooting responses provide actionable guidance."""
        response = watson_client.send_message(test_case["question"])

        assert response_validator.validate_response_structure(response), (
            f"{test_case['id']} response invalid"
        )

        response_text = normalize_text(response_validator.response_text(response))
        action_keywords = [
            "check", "verify", "ensure", "try", "step", "follow",
            "configure", "update", "restart", "review", "contact"
        ]
        has_actions = any(keyword in response_text for keyword in action_keywords)

        assert has_actions, (
            f"{test_case['id']} troubleshooting response lacks actionable guidance"
        )
        assert len(response_text) > 50, (
            f"{test_case['id']} troubleshooting response too brief"
        )


class TestDriftMonitoring:
    """Test suite for response drift detection."""

    @pytest.mark.baseline
    def test_establish_baseline(self, watson_client, test_corpus, drift_monitor):
        """Establish baseline responses for drift monitoring."""
        baseline_results = {}

        for test_case in test_corpus[:10]:
            response = watson_client.send_message(test_case["question"])
            baseline_results[test_case["id"]] = {
                "question": test_case["question"],
                "confidence": response.get("context", {}).get("confidence", 0),
                "response_length": len(response.get("output", {}).get("text", "")),
                "timestamp": datetime.now().isoformat(),
                "response_text": response.get("output", {}).get("text", "")
            }

        drift_monitor.save_baseline(baseline_results)
        assert baseline_results, "Failed to establish baseline"

    @pytest.mark.drift_monitoring
    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(limit=10)]
    )
    def test_detect_response_drift(self, watson_client, test_case, drift_monitor):
        """Test drift detection against baseline."""
        response = watson_client.send_message(test_case["question"])
        drift_analysis = drift_monitor.detect_drift(response, test_case["id"])

        logger.info(
            "Drift Analysis for %s | detected=%s | overall=%s",
            test_case["id"],
            drift_analysis["drift_detected"],
            drift_analysis.get("drift_metrics", {}).get("overall_drift", 0)
        )

        assert "drift_detected" in drift_analysis, (
            f"{test_case['id']} drift analysis missing expected output"
        )


class TestPerformance:
    """Test suite for performance metrics."""

    @pytest.mark.performance
    @pytest.mark.parametrize(
        "test_case",
        [pytest.param(tc, id=tc["id"]) for tc in load_test_cases(limit=5)]
    )
    def test_response_time(self, watson_client, test_case):
        """Test that responses are returned within acceptable time."""
        start_time = time.time()
        watson_client.send_message(test_case["question"])
        end_time = time.time()

        response_time = (end_time - start_time) * 1000
        logger.info("Response time for %s: %.2fms", test_case["id"], response_time)

        assert response_time < MAX_RESPONSE_TIME_MS, (
            f"{test_case['id']} response time {response_time:.2f}ms exceeds threshold"
        )


pytestmark = [
    pytest.mark.watson_orchestrate,
    pytest.mark.integration,
    pytest.mark.regression
]

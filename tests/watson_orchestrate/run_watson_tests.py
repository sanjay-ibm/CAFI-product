#!/usr/bin/env python3
"""
Watson Orchestrate Test Runner (Enhanced)

Features:
- Stronger error handling
- Structured logging
- Cross-platform subprocess safety
- Better .env parsing
- Optional dry-run mode
- Improved command composition
- Richer validation
- Safer summary generation
- Cleaner maintainability
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DEFAULT_TEST_FILE = "test_watson_orchestrate.py"
DEFAULT_RESULTS_DIR = "results"
DEFAULT_WORKERS = 4
ENV_FILE_NAME = ".env"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("watson_test_runner")


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

def load_env_file(env_path: Path) -> None:
    """
    Load environment variables from .env file safely.
    Existing environment variables are not overwritten.
    """
    if not env_path.exists():
        logger.debug("No .env file found at %s", env_path)
        return

    logger.info("Loading environment variables from %s", env_path)

    try:
        with env_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    logger.warning("Skipping malformed line %d in .env", line_number)
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if key and key not in os.environ:
                    os.environ[key] = value

    except Exception as exc:
        logger.error("Failed to load .env file: %s", exc)


def timestamp() -> str:
    """Generate consistent timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_run_command(
    cmd: Sequence[str],
    cwd: Path,
    check: bool = False
) -> subprocess.CompletedProcess:
    """
    Execute subprocess safely with logging.
    """
    logger.info("Executing: %s", shlex.join(cmd))

    try:
        return subprocess.run(
            list(cmd),
            cwd=str(cwd),
            check=check,
            text=True
        )
    except FileNotFoundError:
        logger.error("Command not found: %s", cmd[0])
        raise
    except subprocess.CalledProcessError as exc:
        logger.error("Command failed with code %s", exc.returncode)
        raise


# -----------------------------------------------------------------------------
# Data Classes
# -----------------------------------------------------------------------------

@dataclass
class TestRunConfig:
    test_markers: Optional[List[str]] = None
    test_files: Optional[List[str]] = None
    verbose: bool = False
    html_report: bool = False
    coverage: bool = False
    parallel: bool = False
    workers: int = DEFAULT_WORKERS
    stop_on_fail: bool = False
    keyword: Optional[str] = None
    dry_run: bool = False


# -----------------------------------------------------------------------------
# Main Runner
# -----------------------------------------------------------------------------

class WatsonTestRunner:
    """Enhanced Watson Orchestrate test runner."""

    def __init__(self, test_dir: Optional[Path] = None) -> None:
        self.test_dir = test_dir or Path(__file__).resolve().parent
        self.project_root = self.test_dir.parent.parent
        self.results_dir = self.test_dir / DEFAULT_RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)

        load_env_file(self.test_dir / ENV_FILE_NAME)

    # -------------------------------------------------------------------------
    # Command Builder
    # -------------------------------------------------------------------------

    def build_pytest_command(self, config: TestRunConfig) -> List[str]:
        cmd = ["python", "-m", "pytest"]

        # Test files
        if config.test_files:
            cmd.extend(config.test_files)
        else:
            cmd.append(str(self.test_dir / DEFAULT_TEST_FILE))

        # Markers
        if config.test_markers:
            cmd.extend(["-m", " or ".join(config.test_markers)])

        # Keyword filter
        if config.keyword:
            cmd.extend(["-k", config.keyword])

        # Verbosity
        cmd.append("-v" if config.verbose else "-q")

        # HTML report
        if config.html_report:
            report_file = self.results_dir / f"report_{timestamp()}.html"
            cmd.extend(["--html", str(report_file), "--self-contained-html"])

        # Coverage
        if config.coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=html",
                "--cov-report=term"
            ])

        # Parallel
        if config.parallel:
            cmd.extend(["-n", str(config.workers)])

        # Stop on fail
        if config.stop_on_fail:
            cmd.append("-x")

        # Diagnostics
        cmd.extend([
            "-l",
            "--capture=no"
        ])

        return cmd

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------

    def run_tests(self, config: TestRunConfig) -> int:
        cmd = self.build_pytest_command(config)

        logger.info("=" * 80)
        logger.info("Running Watson Orchestrate Tests")
        logger.info("=" * 80)

        if config.dry_run:
            logger.info("Dry run mode enabled. Command not executed.")
            print(shlex.join(cmd))
            return 0

        try:
            result = safe_run_command(cmd, cwd=self.project_root)
            return result.returncode
        except Exception:
            return 1

    # -------------------------------------------------------------------------
    # Preset Modes
    # -------------------------------------------------------------------------

    def run_baseline_tests(self, **kwargs) -> int:
        logger.info("Running baseline tests...")
        return self.run_tests(
            TestRunConfig(test_markers=["baseline"], **kwargs)
        )

    def run_drift_monitoring(self, **kwargs) -> int:
        logger.info("Running drift monitoring tests...")
        return self.run_tests(
            TestRunConfig(test_markers=["drift_monitoring"], **kwargs)
        )

    def run_performance_tests(self, **kwargs) -> int:
        logger.info("Running performance tests...")
        return self.run_tests(
            TestRunConfig(test_markers=["performance"], **kwargs)
        )

    def run_category_tests(self, category: str, **kwargs) -> int:
        logger.info("Running category tests: %s", category)
        return self.run_tests(
            TestRunConfig(keyword=category, **kwargs)
        )

    def run_quick_tests(self, **kwargs) -> int:
        logger.info("Running quick smoke tests...")
        return self.run_tests(
            TestRunConfig(
                keyword="PS001 or PS002 or GI001",
                stop_on_fail=True,
                **kwargs
            )
        )

    def run_all_tests(self, **kwargs) -> int:
        logger.info("Running full test suite...")
        return self.run_tests(TestRunConfig(**kwargs))

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def check_environment(self) -> bool:
        logger.info("Checking environment configuration...")

        issues = []

        if not os.getenv("WATSON_ORCHESTRATE_API_KEY"):
            issues.append("WATSON_ORCHESTRATE_API_KEY not set")

        corpus_file = self.test_dir / "test_data_corpus.json"
        if not corpus_file.exists():
            issues.append(f"Missing test corpus: {corpus_file}")

        try:
            safe_run_command(["python", "-m", "pytest", "--version"], cwd=self.project_root, check=True)
        except Exception:
            issues.append("pytest is not installed")

        try:
            import requests  # noqa: F401
        except ImportError:
            issues.append("requests library is not installed")

        if issues:
            logger.error("Environment issues detected:")
            for issue in issues:
                logger.error(" - %s", issue)
            return False

        logger.info("Environment is properly configured.")
        return True

    # -------------------------------------------------------------------------
    # Reporting
    # -------------------------------------------------------------------------

    def generate_summary_report(self) -> None:
        logger.info("Generating summary report...")

        result_files = sorted(self.results_dir.glob("test_results_*.json"))

        if not result_files:
            logger.warning("No test results found.")
            return

        latest_result = result_files[-1]

        try:
            with latest_result.open("r", encoding="utf-8") as f:
                results = json.load(f)

            if not isinstance(results, list):
                raise ValueError("Results file must contain a list")

            total = len(results)
            passed = sum(1 for r in results if r.get("status") == "passed")
            failed = sum(1 for r in results if r.get("status") == "failed")

            logger.info("=" * 80)
            logger.info("Test Summary Report")
            logger.info("Source: %s", latest_result.name)
            logger.info("Total: %d", total)
            logger.info("Passed: %d (%.1f%%)", passed, (passed / total * 100) if total else 0)
            logger.info("Failed: %d (%.1f%%)", failed, (failed / total * 100) if total else 0)
            logger.info("=" * 80)

        except Exception as exc:
            logger.error("Failed to generate summary: %s", exc)


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Watson Orchestrate Test Runner"
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument("--all", action="store_true")
    group.add_argument("--baseline", action="store_true")
    group.add_argument("--drift", action="store_true")
    group.add_argument("--performance", action="store_true")
    group.add_argument(
        "--category",
        choices=[
            "product_specific",
            "general_ibm",
            "multi_turn",
            "product_comparison",
            "troubleshooting"
        ]
    )
    group.add_argument("--quick", action="store_true")
    group.add_argument("--check", action="store_true")

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    runner = WatsonTestRunner()

    if args.check:
        sys.exit(0 if runner.check_environment() else 1)

    if args.summary:
        runner.generate_summary_report()
        sys.exit(0)

    if not runner.check_environment():
        sys.exit(1)

    common_args = {
        "verbose": args.verbose,
        "html_report": args.html,
        "coverage": args.coverage,
        "parallel": args.parallel,
        "workers": args.workers,
        "dry_run": args.dry_run
    }

    if args.baseline:
        code = runner.run_baseline_tests(**common_args)
    elif args.drift:
        code = runner.run_drift_monitoring(**common_args)
    elif args.performance:
        code = runner.run_performance_tests(**common_args)
    elif args.category:
        code = runner.run_category_tests(args.category, **common_args)
    elif args.quick:
        code = runner.run_quick_tests(**common_args)
    else:
        code = runner.run_all_tests(**common_args)

    if code == 0:
        logger.info("All tests passed successfully.")
    else:
        logger.error("Tests failed with exit code %d", code)

    sys.exit(code)


if __name__ == "__main__":
    main()

# Made with Bob

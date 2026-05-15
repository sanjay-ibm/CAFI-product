#!/usr/bin/env python3
"""
Quick test runner for Watson Orchestrate - bypasses caching issues
"""
import subprocess
import sys
from pathlib import Path

# Load environment variables from .env file
def load_env():
    import os
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

print("\n🚀 Running Quick Smoke Tests (3 questions)...\n")

# Run pytest with specific test IDs
cmd = [
    "pytest",
    str(Path(__file__).parent / "test_watson_orchestrate.py"),
    "-k", "PS001 or PS002 or GI001",
    "-v",
    "-x",  # Stop on first failure
    "--tb=short"
]

result = subprocess.run(cmd)
sys.exit(result.returncode)

# Made with Bob

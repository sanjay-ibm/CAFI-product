#!/bin/bash
# Watson Orchestrate Test Runner Script (Linux/macOS)
# 
# Usage:
#   ./run_watson_tests.sh --all
#   ./run_watson_tests.sh --baseline
#   ./run_watson_tests.sh --drift
#   ./run_watson_tests.sh --quick

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Load environment variables if .env exists
if [ -f .env ]; then
    echo -e "${BLUE}Loading environment from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Check if pytest is installed
if ! python3 -c "import pytest" &> /dev/null; then
    echo -e "${YELLOW}Warning: pytest is not installed${NC}"
    echo -e "${BLUE}Installing pytest...${NC}"
    pip install pytest pytest-html pytest-xdist requests
fi

# Run the Python test runner
echo -e "${GREEN}Starting Watson Orchestrate Tests${NC}"
python3 run_watson_tests.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Tests completed successfully${NC}"
else
    echo -e "${RED}❌ Tests failed with exit code $exit_code${NC}"
fi

exit $exit_code

# Made with Bob

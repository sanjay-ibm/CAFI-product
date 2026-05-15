#!/bin/bash
# Setup script for automated testing environment
# Usage: ./scripts/setup_testing.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Testing Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r config/requirements.txt
echo -e "${GREEN}Dependencies installed${NC}"
echo ""

# Install pre-commit hooks
echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}Installing pre-commit...${NC}"
    pip install pre-commit
fi

pre-commit install
pre-commit install --hook-type commit-msg
echo -e "${GREEN}Pre-commit hooks installed${NC}"
echo ""

# Make test scripts executable
echo -e "${YELLOW}Making test scripts executable...${NC}"
chmod +x scripts/run_tests.sh
echo -e "${GREEN}Test scripts are now executable${NC}"
echo ""

# Create coverage directory
echo -e "${YELLOW}Creating coverage directory...${NC}"
mkdir -p htmlcov
echo -e "${GREEN}Coverage directory created${NC}"
echo ""

# Run initial test to verify setup
echo -e "${YELLOW}Running initial test to verify setup...${NC}"
if pytest tests/ -v --tb=short -x; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Setup completed successfully! ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Run tests: ./scripts/run_tests.sh"
    echo "  2. Run with coverage: ./scripts/run_tests.sh --html"
    echo "  3. Run specific tests: ./scripts/run_tests.sh --unit"
    echo "  4. Watch mode: ./scripts/run_tests.sh --watch"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Setup verification failed! ✗${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Please check the error messages above${NC}"
    exit 1
fi

# Made with Bob

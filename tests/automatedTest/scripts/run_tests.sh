#!/bin/bash
# Automated test runner script for Product Catalog API
# Usage: ./scripts/run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COVERAGE=true
VERBOSE=false
MARKERS=""
STOP_ON_FAIL=false
PARALLEL=false
REPORT_TYPE="term"

# Print usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -v, --verbose           Verbose output"
    echo "  -q, --quiet             Minimal output"
    echo "  -x, --stop-on-fail      Stop on first failure"
    echo "  -m, --markers MARKERS   Run tests with specific markers (e.g., 'unit', 'integration')"
    echo "  -k, --keyword KEYWORD   Run tests matching keyword expression"
    echo "  -n, --parallel N        Run tests in parallel with N workers"
    echo "  --no-cov                Skip coverage report"
    echo "  --html                  Generate HTML coverage report"
    echo "  --xml                   Generate XML coverage report"
    echo "  --unit                  Run only unit tests"
    echo "  --integration           Run only integration tests"
    echo "  --smoke                 Run only smoke tests"
    echo "  --slow                  Include slow tests"
    echo "  --watch                 Watch mode - rerun on file changes"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            VERBOSE=false
            shift
            ;;
        -x|--stop-on-fail)
            STOP_ON_FAIL=true
            shift
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="$2"
            shift 2
            ;;
        -n|--parallel)
            PARALLEL=true
            PARALLEL_WORKERS="$2"
            shift 2
            ;;
        --no-cov)
            COVERAGE=false
            shift
            ;;
        --html)
            REPORT_TYPE="html"
            shift
            ;;
        --xml)
            REPORT_TYPE="xml"
            shift
            ;;
        --unit)
            MARKERS="unit"
            shift
            ;;
        --integration)
            MARKERS="integration"
            shift
            ;;
        --smoke)
            MARKERS="smoke"
            shift
            ;;
        --slow)
            MARKERS="slow"
            shift
            ;;
        --watch)
            WATCH_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Product Catalog API - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest tests/"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add stop on fail
if [ "$STOP_ON_FAIL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Add markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
    echo -e "${YELLOW}Running tests with markers: $MARKERS${NC}"
fi

# Add keyword
if [ -n "$KEYWORD" ]; then
    PYTEST_CMD="$PYTEST_CMD -k $KEYWORD"
    echo -e "${YELLOW}Running tests matching: $KEYWORD${NC}"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    if ! command -v pytest-xdist &> /dev/null; then
        echo -e "${YELLOW}Warning: pytest-xdist not installed. Installing...${NC}"
        pip install pytest-xdist
    fi
    PYTEST_CMD="$PYTEST_CMD -n $PARALLEL_WORKERS"
    echo -e "${YELLOW}Running tests in parallel with $PARALLEL_WORKERS workers${NC}"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=$REPORT_TYPE"
    if [ "$REPORT_TYPE" = "html" ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
        echo -e "${YELLOW}Coverage report will be generated in htmlcov/${NC}"
    elif [ "$REPORT_TYPE" = "xml" ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=xml"
        echo -e "${YELLOW}Coverage report will be generated as coverage.xml${NC}"
    fi
fi

echo ""

# Watch mode
if [ "$WATCH_MODE" = true ]; then
    if ! command -v pytest-watch &> /dev/null; then
        echo -e "${YELLOW}Installing pytest-watch...${NC}"
        pip install pytest-watch
    fi
    echo -e "${GREEN}Starting watch mode...${NC}"
    ptw -- $PYTEST_CMD
    exit 0
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo -e "${BLUE}Command: $PYTEST_CMD${NC}"
echo ""

if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All tests passed! ✓${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Tests failed! ✗${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi

# Made with Bob

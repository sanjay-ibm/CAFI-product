#!/bin/bash

# Watson Orchestrate Integration Test Script
# Tests the Product Search API endpoints that will be used by Watson Orchestrate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Configuration
API_URL="${API_URL:-https://product-catalog-api-cfai.apps.ocp-ai-dev.cp.fyre.ibm.com}"
LOCAL_URL="${LOCAL_URL:-http://localhost:8000}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Watson Orchestrate Integration Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -e "${YELLOW}Testing: ${name}${NC}"
    echo -e "URL: ${url}"
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        echo -e "Response: ${body:0:200}..."
        echo ""
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected HTTP $expected_status, got $http_code)"
        echo -e "Response: $body"
        echo ""
        return 1
    fi
}

# Function to test with JSON output
test_json_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -e "${YELLOW}Testing: ${name}${NC}"
    echo -e "URL: ${url}"
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        echo ""
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected HTTP $expected_status, got $http_code)"
        echo -e "Response: $body"
        echo ""
        return 1
    fi
}

# Determine which URL to test
echo -e "${BLUE}Select test environment:${NC}"
echo "1. Production API ($API_URL)"
echo "2. Local API ($LOCAL_URL)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "2" ]; then
    BASE_URL=$LOCAL_URL
    echo -e "${YELLOW}Testing LOCAL API${NC}"
else
    BASE_URL=$API_URL
    echo -e "${YELLOW}Testing PRODUCTION API${NC}"
fi
echo ""

# Test counter
PASSED=0
FAILED=0

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
if test_json_endpoint "Health Check" "$BASE_URL/health" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 2: Product Search - Simple Query
echo -e "${BLUE}Test 2: Product Search - Simple Query${NC}"
if test_json_endpoint "Search for 'Cloud Pak'" "$BASE_URL/products/search?query=Cloud%20Pak&limit=5" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 3: Product Search - Product Code
echo -e "${BLUE}Test 3: Product Search - Product Code${NC}"
if test_json_endpoint "Search by product code" "$BASE_URL/products/search?query=5737-H33" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 4: Product Search - Fuzzy Match
echo -e "${BLUE}Test 4: Product Search - Fuzzy Match${NC}"
if test_json_endpoint "Fuzzy search for 'websphere'" "$BASE_URL/products/search?query=websphere&threshold=0.70" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 5: Product Search - High Threshold
echo -e "${BLUE}Test 5: Product Search - High Threshold${NC}"
if test_json_endpoint "High precision search" "$BASE_URL/products/search?query=DB2&threshold=0.90&limit=3" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 6: Product Search - Legacy Format
echo -e "${BLUE}Test 6: Product Search - Legacy Format${NC}"
if test_json_endpoint "Legacy format search" "$BASE_URL/products/search?query=IBM&format=legacy&limit=5" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 7: Get Product by Code (if we know a valid code)
echo -e "${BLUE}Test 7: Get Product by Code${NC}"
if test_json_endpoint "Get product 5737-H33" "$BASE_URL/products/5737-H33" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 8: List Products
echo -e "${BLUE}Test 8: List Products${NC}"
if test_json_endpoint "List products (paginated)" "$BASE_URL/products?limit=10&offset=0" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 9: Invalid Product Code (should return 404)
echo -e "${BLUE}Test 9: Invalid Product Code${NC}"
if test_endpoint "Get invalid product" "$BASE_URL/products/INVALID-CODE-999" 404; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 10: Empty Query (should return 422)
echo -e "${BLUE}Test 10: Empty Query Validation${NC}"
if test_endpoint "Empty query validation" "$BASE_URL/products/search?query=" 422; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 11: OpenAPI Documentation
echo -e "${BLUE}Test 11: OpenAPI Documentation${NC}"
if test_endpoint "OpenAPI docs available" "$BASE_URL/docs" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Test 12: OpenAPI JSON Schema
echo -e "${BLUE}Test 12: OpenAPI JSON Schema${NC}"
if test_json_endpoint "OpenAPI JSON schema" "$BASE_URL/openapi.json" 200; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}The API is ready for Watson Orchestrate integration.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed.${NC}"
    echo -e "${YELLOW}Please fix the issues before deploying to Watson Orchestrate.${NC}"
    exit 1
fi

# Made with Bob

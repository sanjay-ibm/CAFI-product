"""
API endpoint tests for Product Catalog API.

Run with: pytest tests/test_api.py
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and system endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Product Catalog API"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "matcher_loaded" in data
        assert data["status"] == "ok"
        assert data["matcher_loaded"] is True
    
    def test_stats_endpoint(self):
        """Test statistics endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "matcher_type" in data
        assert "exact_match" in data
        assert "fuzzy_match" in data


class TestSearchEndpoints:
    """Test product search endpoints."""
    
    def test_search_with_valid_query(self):
        """Test search with valid query."""
        response = client.get("/products/search?query=IBM")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert "execution_time_ms" in data
        assert data["query"] == "IBM"
    
    def test_search_with_limit(self):
        """Test search with limit parameter."""
        response = client.get("/products/search?query=IBM&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 5
    
    def test_search_legacy_format(self):
        """Test search with legacy format."""
        response = client.get("/products/search?query=IBM&format=legacy")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        if data["results"]:
            result = data["results"][0]
            assert "score" in result
            assert "product_code" in result
            assert "support_desc" in result
            assert "support_alias" in result
    
    def test_search_with_invalid_limit(self):
        """Test search with invalid limit."""
        response = client.get("/products/search?query=IBM&limit=1000")
        assert response.status_code == 422  # Validation error
    
    def test_search_with_empty_query(self):
        """Test search with empty query."""
        response = client.get("/products/search?query=")
        assert response.status_code == 422  # Validation error


class TestProductEndpoints:
    """Test product listing and retrieval endpoints."""
    
    def test_list_products(self):
        """Test listing all products."""
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "total_available" in data
        assert "products" in data
        assert isinstance(data["products"], list)
    
    def test_list_products_with_pagination(self):
        """Test product listing with pagination."""
        response = client.get("/products?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10
    
    def test_get_product_by_code(self):
        """Test getting product by code."""
        # First get a product code from the list
        list_response = client.get("/products?limit=1")
        if list_response.json()["products"]:
            product_code = list_response.json()["products"][0]["product_code"]
            
            # Now get that specific product
            response = client.get(f"/products/{product_code}")
            assert response.status_code == 200
            data = response.json()
            assert data["product_code"] == product_code
    
    def test_get_nonexistent_product(self):
        """Test getting non-existent product."""
        response = client.get("/products/NONEXISTENT-CODE-12345")
        assert response.status_code == 404


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Product Catalog API"
    
    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_endpoint(self):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200


# Made with Bob
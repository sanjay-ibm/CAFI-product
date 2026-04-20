"""
Unit tests for ProductMatcher core logic.

Run with: pytest tests/test_matcher.py
"""

import pytest
from src.core.matcher import ProductMatcher


@pytest.fixture
def sample_dictionary():
    """Sample product dictionary for testing."""
    return {
        "exact_match": {
            "ibm cloud pak": [
                {
                    "SLC_CODE": "5737-H33",
                    "PRODUCT_NAME": "IBM Cloud Pak for Data"
                }
            ],
            "watson": [
                {
                    "SLC_CODE": "5737-I23",
                    "PRODUCT_NAME": "IBM Watson Studio"
                }
            ]
        },
        "fuzzy_match": {
            "cloud platform": [
                {
                    "SLC_CODE": "5737-H33",
                    "PRODUCT_NAME": "IBM Cloud Pak for Data"
                }
            ]
        }
    }


@pytest.fixture
def matcher(sample_dictionary):
    """Create a ProductMatcher instance for testing."""
    delimiter_dict = {
        "cloud pak": "_"
    }
    return ProductMatcher(
        match_dictionary=sample_dictionary,
        delimiter_dict=delimiter_dict,
        use_enhanced=True
    )


class TestMatcherInitialization:
    """Test matcher initialization."""
    
    def test_matcher_creation(self, matcher):
        """Test matcher is created successfully."""
        assert matcher is not None
        assert matcher.use_enhanced is True
    
    def test_exact_index_populated(self, matcher):
        """Test exact index is populated."""
        assert len(matcher.exact_index) > 0
    
    def test_fuzzy_aliases_populated(self, matcher):
        """Test fuzzy aliases are populated."""
        assert len(matcher.fuzzy_aliases) > 0


class TestTextNormalization:
    """Test text normalization functions."""
    
    def test_clean_string_basic(self, matcher):
        """Test basic string cleaning."""
        result = matcher.clean_string("IBM Cloud Pak")
        assert result == "ibm cloud_pak"
    
    def test_clean_string_special_chars(self, matcher):
        """Test cleaning with special characters."""
        result = matcher.clean_string("IBM's Cloud-Pak!")
        assert "ibm" in result
        assert "cloud" in result
    
    def test_clean_string_whitespace(self, matcher):
        """Test whitespace normalization."""
        result = matcher.clean_string("IBM   Cloud    Pak")
        assert "  " not in result


class TestExactMatching:
    """Test exact matching functionality."""
    
    def test_exact_match_found(self, matcher):
        """Test exact match is found."""
        results = matcher.identify_products("IBM Cloud Pak", fuzzy_threshold=0.7)
        assert len(results) > 0
        assert results[0]["score"] == 1.0
    
    def test_exact_match_case_insensitive(self, matcher):
        """Test exact match is case insensitive."""
        results = matcher.identify_products("ibm cloud pak", fuzzy_threshold=0.7)
        assert len(results) > 0
        assert results[0]["score"] == 1.0


class TestFuzzyMatching:
    """Test fuzzy matching functionality."""
    
    def test_fuzzy_match_found(self, matcher):
        """Test fuzzy match is found."""
        results = matcher.identify_products("cloud platform", fuzzy_threshold=0.6)
        assert len(results) > 0
    
    def test_fuzzy_threshold_respected(self, matcher):
        """Test fuzzy threshold is respected."""
        # High threshold should return fewer results
        results_high = matcher.identify_products("cloud", fuzzy_threshold=0.9)
        results_low = matcher.identify_products("cloud", fuzzy_threshold=0.5)
        assert len(results_low) >= len(results_high)


class TestResultFormatting:
    """Test result formatting."""
    
    def test_result_structure(self, matcher):
        """Test result has correct structure."""
        results = matcher.identify_products("IBM Cloud Pak")
        if results:
            result = results[0]
            assert "score" in result
            assert "product_code" in result
            assert "product_name" in result
            assert "matched_aliases" in result
            assert "match_types" in result
    
    def test_result_limit(self, matcher):
        """Test result limit is respected."""
        results = matcher.identify_products("cloud", return_count=2)
        assert len(results) <= 2


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_query(self, matcher):
        """Test empty query returns empty results."""
        results = matcher.identify_products("")
        assert len(results) == 0
    
    def test_very_short_query(self, matcher):
        """Test very short query."""
        results = matcher.identify_products("a")
        # Should return results or empty list, not crash
        assert isinstance(results, list)
    
    def test_special_characters_only(self, matcher):
        """Test query with only special characters."""
        results = matcher.identify_products("!@#$%")
        assert isinstance(results, list)
    
    def test_unicode_characters(self, matcher):
        """Test query with unicode characters."""
        results = matcher.identify_products("IBM™ Cloud®")
        assert isinstance(results, list)


# Made with Bob
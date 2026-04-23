"""
Unit tests for the Confidence Scorer module.

Tests cover:
- Base score calculation for different match types
- Penalty application (disambiguation, generic terms, fallback)
- Boost application (platform keywords, session history, model numbers)
- Score capping at 1.00
- Two decimal precision
"""

import pytest
from src.core.confidence_scorer import ConfidenceScorer


class TestConfidenceScorer:
    """Test suite for ConfidenceScorer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = ConfidenceScorer()
    
    def test_exact_match_single_product(self):
        """Test base score for exact match with single product."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="ibm cloud pak for data",
            matched_alias="ibm cloud pak for data",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90, no penalties, no boosts
        assert confidence == 0.90
    
    def test_exact_match_multiple_products(self):
        """Test base score for exact match with multiple products."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_phrase",
            match_score=1.0,
            query="db2",
            matched_alias="db2",
            product_count=3,
            candidate_count=3,
            product_code="5724-Y31",
            used_fallback=False
        )
        # Base: 0.75, penalty: -0.10 (multiple candidates)
        assert confidence == 0.65
    
    def test_substring_match_long_key(self):
        """Test base score for substring match with long alias."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy_bm25",
            match_score=0.90,
            query="ibm cloud pak for data on openshift",
            matched_alias="ibm cloud pak for data",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.70 (long alias >= 10 chars, score >= 0.85)
        assert confidence == 0.70
    
    def test_token_overlap_only(self):
        """Test base score for basic token overlap."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy",
            match_score=0.72,
            query="cloud database",
            matched_alias="cloud pak",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.50 (token overlap, score < 0.80)
        assert confidence == 0.50
    
    def test_multiple_candidates_penalty(self):
        """Test penalty for multiple candidate products."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="watson",
            matched_alias="watson",
            product_count=1,
            candidate_count=5,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90, penalty: -0.10 (multiple candidates)
        assert confidence == 0.80
    
    def test_generic_terms_penalty(self):
        """Test penalty for matches relying on generic terms."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy",
            match_score=0.75,
            query="software solution",
            matched_alias="software solution",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.50, penalty: -0.10 (generic terms)
        assert confidence == 0.40
    
    def test_fallback_logic_penalty(self):
        """Test penalty for using fallback token logic."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy_ngram",
            match_score=0.65,
            query="ibm clod",  # typo
            matched_alias="ibm cloud",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=True
        )
        # Base: 0.50, penalty: -0.15 (fallback)
        assert confidence == 0.35
    
    def test_platform_keywords_boost(self):
        """Test boost for platform/version keyword alignment."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="ibm cloud pak for data on z/os",
            matched_alias="ibm cloud pak for data z/os",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90, boost: +0.05 (platform keyword: z/os)
        assert confidence == 0.95
    
    def test_session_history_boost(self):
        """Test boost for previously confirmed product."""
        scorer = ConfidenceScorer(session_history={"5737-H33"})
        confidence = scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="cloud pak for data",
            matched_alias="cloud pak for data",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90, boost: +0.05 (session history)
        assert confidence == 0.95
    
    def test_model_number_boost(self):
        """Test boost for explicit model number mention."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="ibm z15 mainframe",
            matched_alias="ibm z15",
            product_count=1,
            candidate_count=1,
            product_code="2964-N63",
            used_fallback=False
        )
        # Base: 0.90, boost: +0.05 (model number: z15)
        assert confidence == 0.95
    
    def test_combined_penalties_and_boosts(self):
        """Test combined penalties and boosts."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy_bm25",
            match_score=0.85,
            query="ibm cloud software on kubernetes",
            matched_alias="ibm cloud software",
            product_count=2,
            candidate_count=5,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.60 (fuzzy, score >= 0.80)
        # Penalties: -0.10 (multiple candidates) -0.10 (generic: software)
        # Boosts: +0.05 (platform: cloud, kubernetes)
        # Total: 0.60 - 0.20 + 0.05 = 0.45
        assert confidence == 0.45
    
    def test_score_capped_at_one(self):
        """Test that confidence score is capped at 1.00."""
        scorer = ConfidenceScorer(session_history={"5737-H33"})
        confidence = scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="ibm cloud pak for data v4.5 on openshift",
            matched_alias="ibm cloud pak for data openshift",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90
        # Boosts: +0.05 (platform: cloud, openshift) +0.05 (session) +0.05 (version: v4.5)
        # Total: 0.90 + 0.15 = 1.05, capped at 1.00
        assert confidence == 1.00
    
    def test_two_decimal_precision(self):
        """Test that confidence scores have exactly 2 decimal places."""
        confidence = self.scorer.calculate_confidence(
            match_type="fuzzy",
            match_score=0.777,
            query="database",
            matched_alias="db",
            product_count=1,
            candidate_count=1,
            product_code="5724-Y31",
            used_fallback=False
        )
        # Verify 2 decimal precision
        assert len(str(confidence).split('.')[-1]) <= 2
    
    def test_ibm_product_code_detection(self):
        """Test detection of IBM product codes as model numbers."""
        confidence = self.scorer.calculate_confidence(
            match_type="exact_full",
            match_score=1.0,
            query="5737-H33 cloud pak",
            matched_alias="cloud pak",
            product_count=1,
            candidate_count=1,
            product_code="5737-H33",
            used_fallback=False
        )
        # Base: 0.90, boost: +0.05 (model number: 5737-H33)
        assert confidence == 0.95
    
    def test_session_history_management(self):
        """Test session history add and clear operations."""
        scorer = ConfidenceScorer()
        
        # Initially empty
        assert len(scorer.session_history) == 0
        
        # Add product
        scorer.add_to_session_history("5737-H33")
        assert "5737-H33" in scorer.session_history
        
        # Add another
        scorer.add_to_session_history("5724-Y31")
        assert len(scorer.session_history) == 2
        
        # Clear
        scorer.clear_session_history()
        assert len(scorer.session_history) == 0
    
    def test_confidence_explanation(self):
        """Test confidence explanation generation."""
        explanation = self.scorer.get_confidence_explanation(
            match_type="exact_full",
            base_score=0.90,
            penalties=0.10,
            boosts=0.05,
            final_score=0.85
        )
        
        assert explanation["match_type"] == "exact_full"
        assert explanation["base_score"] == 0.90
        assert explanation["penalties"] == 0.10
        assert explanation["boosts"] == 0.05
        assert explanation["final_score"] == 0.85
        assert "0.90 - 0.10 + 0.05 = 0.85" in explanation["calculation"]


# Made with Bob
"""
Manual test script for confidence scorer (no pytest required).
"""

from src.core.confidence_scorer import ConfidenceScorer


def test_confidence_scorer():
    """Run manual tests for confidence scorer."""
    print("=" * 60)
    print("Testing Confidence Scorer Implementation")
    print("=" * 60)
    
    scorer = ConfidenceScorer()
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Exact match, single product
    print("\n1. Exact match, single product (Base: 0.90)")
    confidence = scorer.calculate_confidence(
        match_type="exact_full",
        match_score=1.0,
        query="ibm db2 database",
        matched_alias="ibm db2 database",
        product_count=1,
        candidate_count=1,
        product_code="5724-Y31",
        used_fallback=False
    )
    print(f"   Expected: 0.90, Got: {confidence}")
    if confidence == 0.90:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 2: Exact match, multiple products with penalty
    print("\n2. Exact match, multiple products (Base: 0.75, Penalty: -0.10)")
    confidence = scorer.calculate_confidence(
        match_type="exact_phrase",
        match_score=1.0,
        query="db2",
        matched_alias="db2",
        product_count=3,
        candidate_count=3,
        product_code="5724-Y31",
        used_fallback=False
    )
    print(f"   Expected: 0.65, Got: {confidence}")
    if confidence == 0.65:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 3: Substring match (long key)
    print("\n3. Substring match, long key (Base: 0.70)")
    confidence = scorer.calculate_confidence(
        match_type="fuzzy_bm25",
        match_score=0.90,
        query="ibm mainframe database system",
        matched_alias="ibm mainframe database",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=False
    )
    print(f"   Expected: 0.70, Got: {confidence}")
    if confidence == 0.70:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 4: Token overlap only
    print("\n4. Token overlap only (Base: 0.50)")
    confidence = scorer.calculate_confidence(
        match_type="fuzzy",
        match_score=0.72,
        query="database system",
        matched_alias="database manager",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=False
    )
    print(f"   Expected: 0.50, Got: {confidence}")
    if confidence == 0.50:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 5: Fallback penalty
    print("\n5. Fallback logic penalty (Base: 0.50, Penalty: -0.15)")
    confidence = scorer.calculate_confidence(
        match_type="fuzzy_ngram",
        match_score=0.65,
        query="ibm database",
        matched_alias="ibm db",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=True
    )
    print(f"   Expected: 0.35, Got: {confidence}")
    if confidence == 0.35:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 6: Platform keyword boost
    print("\n6. Platform keyword boost (Base: 0.90, Boost: +0.05)")
    confidence = scorer.calculate_confidence(
        match_type="exact_full",
        match_score=1.0,
        query="ibm database on z/os",
        matched_alias="ibm database z/os",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=False
    )
    print(f"   Expected: 0.95, Got: {confidence}")
    if confidence == 0.95:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 7: Session history boost
    print("\n7. Session history boost (Base: 0.90, Boost: +0.05)")
    scorer_with_history = ConfidenceScorer(session_history={"5737-H33"})
    confidence = scorer_with_history.calculate_confidence(
        match_type="exact_full",
        match_score=1.0,
        query="database manager",
        matched_alias="database manager",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=False
    )
    print(f"   Expected: 0.95, Got: {confidence}")
    if confidence == 0.95:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 8: Model number boost
    print("\n8. Model number boost (Base: 0.90, Boost: +0.05)")
    confidence = scorer.calculate_confidence(
        match_type="exact_full",
        match_score=1.0,
        query="ibm z15 mainframe",
        matched_alias="ibm z15",
        product_count=1,
        candidate_count=1,
        product_code="2964-N63",
        used_fallback=False
    )
    print(f"   Expected: 0.95, Got: {confidence}")
    if confidence == 0.95:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 9: Score capped at 1.00
    print("\n9. Score capped at 1.00 (Base: 0.90, Boosts: +0.15 = 1.05 -> 1.00)")
    scorer_with_history = ConfidenceScorer(session_history={"5737-H33"})
    confidence = scorer_with_history.calculate_confidence(
        match_type="exact_full",
        match_score=1.0,
        query="ibm database v4.5 on openshift",
        matched_alias="ibm database openshift",
        product_count=1,
        candidate_count=1,
        product_code="5737-H33",
        used_fallback=False
    )
    print(f"   Expected: 1.00, Got: {confidence}")
    if confidence == 1.00:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Test 10: Two decimal precision
    print("\n10. Two decimal precision check")
    confidence = scorer.calculate_confidence(
        match_type="fuzzy",
        match_score=0.777,
        query="database",
        matched_alias="db",
        product_count=1,
        candidate_count=1,
        product_code="5724-Y31",
        used_fallback=False
    )
    decimal_places = len(str(confidence).split('.')[-1]) if '.' in str(confidence) else 0
    print(f"   Confidence: {confidence}, Decimal places: {decimal_places}")
    if decimal_places <= 2:
        print("   [PASSED]")
        tests_passed += 1
    else:
        print(f"   [FAILED]")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)
    
    if tests_failed == 0:
        print("\nAll tests PASSED!")
        print("\nConfidence Scoring Rules Summary:")
        print("  Base Scores:")
        print("    - Exact match, single product: 0.90")
        print("    - Exact match, multiple products: 0.75")
        print("    - Substring match (long key): 0.70")
        print("    - Token overlap only: 0.50")
        print("  Penalties:")
        print("    - Multiple candidates: -0.10")
        print("    - Generic terms: -0.10")
        print("    - Fallback logic: -0.15")
        print("  Boosts:")
        print("    - Platform keywords: +0.05")
        print("    - Session history: +0.05")
        print("    - Model number: +0.05")
        print("  Score capped at 1.00 with 2 decimal precision")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1


if __name__ == "__main__":
    exit(test_confidence_scorer())

# Made with Bob

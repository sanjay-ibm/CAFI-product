# Confidence Scoring System

## Overview

The Product ID Agent uses a sophisticated confidence scoring system to provide transparency and reliability in product identification. Each match receives a confidence score between **0.00 and 1.00** (with two decimal precision) that reflects the quality and certainty of the match.

## Scoring Components

The confidence score is calculated using three main components:

```
Confidence = Base Score - Penalties + Boosts
(capped at 1.00, rounded to 2 decimal places)
```

### 1. Base Score (Primary Driver)

The base score is determined by the **match strength** and **product count**:

| Condition | Base Score |
|-----------|------------|
| Exact dictionary key match, single product | 0.90 |
| Exact match, multiple products | 0.75 |
| Substring match (long key, ≥10 chars) | 0.70 |
| Token overlap only | 0.50 |

**Examples:**

- Query: "IBM Cloud Pak for Data" → Exact match to single product → **0.90**
- Query: "DB2" → Exact match to 3 products → **0.75**
- Query: "IBM mainframe database system" → Matches "IBM mainframe database" (23 chars) → **0.70**
- Query: "cloud database" → Token overlap with "cloud pak" → **0.50**

### 2. Disambiguation Penalties

Penalties are subtracted when there's ambiguity or uncertainty:

| Penalty Type | Deduction | When Applied |
|--------------|-----------|--------------|
| Multiple candidate products | -0.10 | More than 1 product remains after matching |
| Generic terms relied upon | -0.10 | Match depends heavily on generic words (software, product, solution, etc.) |
| Fallback token logic used | -0.15 | N-gram or low-score fuzzy matching was required |

**Examples:**

- Query: "Watson" → 5 products match → Penalty: **-0.10**
- Query: "software solution" → Generic terms dominate → Penalty: **-0.10**
- Query: "ibm clod" (typo) → N-gram fallback used → Penalty: **-0.15**

### 3. Contextual Boosts

Boosts are added when there's additional supporting evidence:

| Boost Type | Addition | When Applied |
|------------|----------|--------------|
| Platform/version keywords | +0.05 | Keywords like z/os, cloud, saas, kubernetes align in query and alias |
| Previously confirmed product | +0.05 | Product was confirmed in current session |
| Model number mentioned | +0.05 | Query contains explicit model/version numbers (5737-H33, v4.5, z15) |

**Examples:**

- Query: "IBM database on z/os" → Platform keyword "z/os" → Boost: **+0.05**
- Query: "Cloud Pak for Data" → Previously confirmed in session → Boost: **+0.05**
- Query: "IBM z15 mainframe" → Model number "z15" → Boost: **+0.05**

## Calculation Examples

### Example 1: High Confidence Match
```
Query: "IBM Cloud Pak for Data"
Match: Exact match to single product
Platform: "cloud" keyword present

Base Score:    0.90 (exact match, single product)
Penalties:     0.00 (no ambiguity)
Boosts:       +0.05 (platform keyword)
─────────────────────
Confidence:    0.95
```

### Example 2: Medium Confidence Match
```
Query: "Watson AI"
Match: Exact match to 5 products
Generic: "AI" is somewhat generic

Base Score:    0.75 (exact match, multiple products)
Penalties:    -0.10 (multiple candidates)
Boosts:        0.00 (no contextual signals)
─────────────────────
Confidence:    0.65
```

### Example 3: Low Confidence Match
```
Query: "software solution"
Match: Fuzzy match via token overlap
Generic: Both terms are generic

Base Score:    0.50 (token overlap)
Penalties:    -0.10 (generic terms)
Boosts:        0.00 (no contextual signals)
─────────────────────
Confidence:    0.40
```

### Example 4: Maximum Confidence
```
Query: "IBM Cloud Pak for Data v4.5 on OpenShift"
Match: Exact match to single product (previously confirmed)
Platform: "cloud" and "openshift" keywords
Version: "v4.5" version number

Base Score:    0.90 (exact match, single product)
Penalties:     0.00 (no ambiguity)
Boosts:       +0.15 (platform +0.05, session +0.05, version +0.05)
─────────────────────
Raw Score:     1.05
Confidence:    1.00 (capped)
```

## Platform Keywords

The following keywords trigger the platform/version boost when they appear in both the query and matched alias:

**Operating Systems:**
- z/os, zos, z os
- linux, windows, unix, aix

**Cloud Platforms:**
- cloud, saas, paas, iaas
- kubernetes, k8s, openshift
- hybrid, multicloud, multi-cloud

**Deployment Types:**
- on-premises, on premises, onprem

## Generic Terms

These terms reduce confidence when they dominate the match:

- software, product, solution, system, tool
- application, platform, service, program
- suite, package, bundle, offering

## Model Number Patterns

The following patterns are recognized as model numbers:

1. **IBM Product Codes:** `5737-H33`, `5724-Y31`
2. **Version Numbers:** `v1.0`, `version 2.5`, `4.5`
3. **Model Numbers:** `z15`, `z14`, `p9`

## API Response Format

The confidence score is included in all API responses:

```json
{
  "query": "IBM Cloud Pak for Data",
  "results": [
    {
      "score": 1.0,
      "confidence": 0.95,
      "product_code": "5737-H33",
      "product_name": "IBM Cloud Pak for Data",
      "matched_aliases": ["ibm cloud pak for data"],
      "match_types": ["exact_full"]
    }
  ]
}
```

**Fields:**
- `score`: Raw match score from the matcher (0.0-1.0)
- `confidence`: Adjusted confidence score with contextual factors (0.00-1.00)

## Session History

The confidence scorer maintains session history to boost confidence for previously confirmed products:

```python
from src.core.confidence_scorer import ConfidenceScorer

# Initialize with session history
scorer = ConfidenceScorer(session_history={"5737-H33", "5724-Y31"})

# Add confirmed product
scorer.add_to_session_history("5655-Y04")

# Clear session
scorer.clear_session_history()
```

## Usage in Code

### Basic Usage

```python
from src.core.confidence_scorer import ConfidenceScorer

scorer = ConfidenceScorer()

confidence = scorer.calculate_confidence(
    match_type="exact_full",
    match_score=1.0,
    query="IBM Cloud Pak for Data",
    matched_alias="ibm cloud pak for data",
    product_count=1,
    candidate_count=1,
    product_code="5737-H33",
    used_fallback=False
)

print(f"Confidence: {confidence}")  # Output: 0.90
```

### With Explanation

```python
explanation = scorer.get_confidence_explanation(
    match_type="exact_full",
    base_score=0.90,
    penalties=0.10,
    boosts=0.05,
    final_score=0.85
)

print(explanation)
# {
#   "match_type": "exact_full",
#   "base_score": 0.90,
#   "penalties": 0.10,
#   "boosts": 0.05,
#   "final_score": 0.85,
#   "calculation": "0.90 - 0.10 + 0.05 = 0.85"
# }
```

## Integration with Matchers

The confidence scoring is automatically integrated into both matcher classes:

```python
from src.core.matcher import ProductMatcher

# Initialize with confidence scoring enabled (default)
matcher = ProductMatcher(
    match_dictionary=data,
    enable_confidence_scoring=True
)

# Results include confidence scores
results = matcher.identify_products("IBM Cloud Pak for Data")
print(results[0]["confidence"])  # 0.95
```

## Best Practices

1. **Use confidence scores for ranking:** Sort results by confidence when multiple matches exist
2. **Set thresholds:** Consider confidence < 0.50 as low-quality matches
3. **Leverage session history:** Track confirmed products to improve subsequent matches
4. **Monitor generic terms:** Flag matches that rely heavily on generic terms
5. **Combine with match score:** Use both `score` and `confidence` for comprehensive evaluation

## Testing

Run the confidence scorer tests:

```bash
python test_confidence_manual.py
```

This validates all scoring rules and edge cases.

---

**Made with Bob**
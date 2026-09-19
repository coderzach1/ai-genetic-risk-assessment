import pytest
from risk_engine import assess_risk, recommendations, validate_inputs

ANCESTRY = {"European": 25, "African": 25, "East Asian": 25, "South Asian": 25}
ENVIRONMENT = {"Food access": 2, "Activity barriers": 2, "Air quality": 2, "Care barriers": 2}
CLINICAL = {"Blood pressure": 2, "Metabolic markers": 2, "Smoking exposure": 0}

def test_result_is_bounded_and_interval_contains_estimate():
    result = assess_risk("Coronary artery disease", 78, ANCESTRY, ENVIRONMENT, CLINICAL, 1, 3, 3)
    assert 1 <= result.lower_bound <= result.adjusted_percentile <= result.upper_bound <= 99
    assert 20 <= result.data_quality <= 95

def test_better_evidence_narrows_uncertainty():
    low = assess_risk("Type 2 diabetes", 70, ANCESTRY, ENVIRONMENT, CLINICAL, 1, 0, 0)
    high = assess_risk("Type 2 diabetes", 70, ANCESTRY, ENVIRONMENT, CLINICAL, 1, 4, 4)
    assert high.upper_bound - high.lower_bound < low.upper_bound - low.lower_bound
    assert high.data_quality > low.data_quality

def test_family_and_clinical_burden_raise_estimate():
    low = assess_risk("Breast cancer", 60, ANCESTRY, ENVIRONMENT, {key: 0 for key in CLINICAL}, 0, 4, 4)
    high = assess_risk("Breast cancer", 60, ANCESTRY, ENVIRONMENT, {key: 4 for key in CLINICAL}, 2, 4, 4)
    assert high.adjusted_percentile > low.adjusted_percentile

def test_invalid_ancestry_is_rejected():
    bad = dict(ANCESTRY); bad["European"] = 24
    with pytest.raises(ValueError, match="total 100"):
        assess_risk("Alzheimer's disease", 50, bad, ENVIRONMENT, CLINICAL, 0, 4, 4)

def test_recommendations_are_actionable():
    result = assess_risk("Type 2 diabetes", 80, ANCESTRY, ENVIRONMENT, CLINICAL, 2, 4, 4)
    assert len(recommendations("Type 2 diabetes", result)) >= 3

def test_validation_reports_out_of_range_values():
    assert validate_inputs(101, ANCESTRY, ENVIRONMENT, CLINICAL)

"""Transparent research-only genetic risk context engine."""

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Mapping

CONDITION_WEIGHTS = {
    "Coronary artery disease": {"family": 0.10, "clinical": 0.15, "environment": 0.08},
    "Type 2 diabetes": {"family": 0.09, "clinical": 0.17, "environment": 0.10},
    "Breast cancer": {"family": 0.16, "clinical": 0.08, "environment": 0.04},
    "Alzheimer's disease": {"family": 0.14, "clinical": 0.08, "environment": 0.05},
}

@dataclass(frozen=True)
class RiskResult:
    adjusted_percentile: float
    lower_bound: float
    upper_bound: float
    data_quality: float
    category: str
    contributions: dict[str, float]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)

def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

def validate_inputs(raw_percentile: float, ancestry: Mapping[str, int], environment: Mapping[str, int], clinical: Mapping[str, int]) -> list[str]:
    errors: list[str] = []
    if not 1 <= raw_percentile <= 99:
        errors.append("PRS percentile must be between 1 and 99.")
    if sum(ancestry.values()) != 100:
        errors.append(f"Ancestry percentages must total 100% (currently {sum(ancestry.values())}%).")
    if any(not 0 <= value <= 100 for value in ancestry.values()):
        errors.append("Each ancestry percentage must be between 0 and 100.")
    if any(not 0 <= value <= 4 for value in environment.values()):
        errors.append("Environment ratings must be between 0 and 4.")
    if any(not 0 <= value <= 4 for value in clinical.values()):
        errors.append("Clinical ratings must be between 0 and 4.")
    return errors

def assess_risk(condition: str, raw_percentile: float, ancestry: Mapping[str, int], environment: Mapping[str, int], clinical: Mapping[str, int], family_history: int, prs_cohort_match: int, variant_quality: int) -> RiskResult:
    """Create a bounded contextual estimate with an explicit uncertainty interval."""
    errors = validate_inputs(raw_percentile, ancestry, environment, clinical)
    if errors:
        raise ValueError(" ".join(errors))
    if condition not in CONDITION_WEIGHTS:
        raise ValueError("Unsupported condition.")
    weights = CONDITION_WEIGHTS[condition]
    environment_load = sum(environment.values()) / max(1, len(environment) * 4)
    clinical_load = sum(clinical.values()) / max(1, len(clinical) * 4)
    family_load = _clamp(family_history / 2, 0, 1)
    cohort_quality = _clamp(prs_cohort_match / 4, 0, 1)
    variant_quality_score = _clamp(variant_quality / 4, 0, 1)
    largest_ancestry_share = max(ancestry.values()) / 100
    representation_quality = 0.55 * cohort_quality + 0.25 * variant_quality_score + 0.20 * largest_ancestry_share
    genetic_effect = ((raw_percentile - 50) / 49) * (0.55 + 0.45 * representation_quality)
    family_effect = (family_load - 0.25) * weights["family"]
    clinical_effect = (clinical_load - 0.50) * weights["clinical"]
    environment_effect = (environment_load - 0.50) * weights["environment"]
    adjusted = _clamp(50 + 49 * (genetic_effect + family_effect + clinical_effect + environment_effect), 1, 99)
    completeness = (cohort_quality + variant_quality_score) / 2
    uncertainty = 5 + (1 - representation_quality) * 16 + (1 - completeness) * 8
    uncertainty += sqrt(abs(adjusted - raw_percentile)) * 0.8
    lower, upper = _clamp(adjusted - uncertainty, 1, 99), _clamp(adjusted + uncertainty, 1, 99)
    quality = _clamp(100 - uncertainty * 2.3, 20, 95)
    category = "Lower" if adjusted < 30 else "Intermediate" if adjusted < 70 else "Higher"
    warnings: list[str] = []
    if cohort_quality < 0.5:
        warnings.append("The PRS reference cohort may not represent this profile; uncertainty is wider.")
    if variant_quality_score < 0.5:
        warnings.append("Variant quality is limited; confirm genotyping and imputation quality.")
    if lower < 70 < upper or lower < 30 < upper:
        warnings.append("The uncertainty interval crosses a category boundary.")
    contributions = {
        "Genetic score": round(genetic_effect * 49, 1),
        "Family history": round(family_effect * 49, 1),
        "Clinical factors": round(clinical_effect * 49, 1),
        "Environment/access": round(environment_effect * 49, 1),
    }
    return RiskResult(round(adjusted, 1), round(lower, 1), round(upper, 1), round(quality, 1), category, contributions, tuple(warnings))

def recommendations(condition: str, result: RiskResult) -> list[str]:
    steps = ["Review the original PRS report, reference cohort, and variant-quality summary."]
    if result.category == "Higher":
        steps.append("Discuss guideline-based screening with a qualified clinician or genetic counselor.")
    elif result.category == "Intermediate":
        steps.append("Combine this estimate with measured clinical risk factors before making decisions.")
    else:
        steps.append("Maintain routine prevention; a lower estimate does not mean zero risk.")
    if result.data_quality < 60:
        steps.append("Improve missing or low-quality inputs before interpreting the estimate.")
    steps.append(f"Use validated {condition.lower()} guidelines for any clinical action.")
    return steps

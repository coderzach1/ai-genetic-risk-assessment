"""Evidence-linked interpretation for PGS005336; not a diagnostic model."""
from dataclasses import asdict, dataclass
from datetime import date
from math import erf, exp, sqrt

MODEL = {"id":"PGS005336","name":"D_MetPRS_SAS","trait":"Type 2 diabetes","method":"LDpred2","genome_build":"GRCh37","variant_count":1_297_046,"or_per_sd":1.78,"beta_per_sd":0.57931,"auroc_low":0.72007,"auroc_high":0.839,"catalog_url":"https://www.pgscatalog.org/score/PGS005336/"}

@dataclass(frozen=True)
class PGSResult:
    percentile: float
    relative_odds: float
    band: str
    quality_score: int
    warnings: tuple[str, ...]
    def to_dict(self) -> dict: return asdict(self)

@dataclass(frozen=True)
class UploadReport:
    ready: bool
    message: str
    filename: str
    genome_build: str
    checks: dict[str, bool]
    def to_dict(self) -> dict: return asdict(self)

def interpret_score(z_score: float, variant_coverage: int, ancestry_match: str, genome_build: str, source: str) -> PGSResult:
    if not -5 <= z_score <= 5: raise ValueError("Standardized PGS must be between -5 and 5.")
    if not 0 <= variant_coverage <= 100: raise ValueError("Variant coverage must be between 0 and 100.")
    percentile = 100 * 0.5 * (1 + erf(z_score / sqrt(2)))
    relative_odds = exp(MODEL["beta_per_sd"] * z_score)
    band = "Lower" if percentile < 20 else "Typical" if percentile < 80 else "Higher"
    quality, warnings = 100, []
    if variant_coverage < 95:
        quality -= min(45, round((95 - variant_coverage) * 1.5)); warnings.append("Variant coverage is below 95%; the score may be unstable.")
    if ancestry_match != "South Asian":
        quality -= 25; warnings.append("PGS005336 is optimized for South Asian ancestry; transferability may be reduced.")
    if genome_build != MODEL["genome_build"]:
        quality -= 20; warnings.append("PGS005336 uses GRCh37; confirm validated liftover and allele harmonization.")
    if source in {"Unknown", "Research pipeline"}:
        quality -= 15; warnings.append("The score source is not a verified clinical genetics laboratory.")
    warnings.append("Relative odds are not absolute disease probability and cannot diagnose diabetes.")
    return PGSResult(round(percentile,1), round(relative_odds,2), band, max(0,quality), tuple(warnings))

def validate_genotype_upload(filename: str, size_bytes: int, genome_build: str) -> UploadReport:
    supported = filename.lower().endswith((".vcf",".vcf.gz",".pgen",".bed")); nonempty = size_bytes > 0; build_ok = genome_build == MODEL["genome_build"]
    ready = supported and nonempty and build_ok
    if not supported: message = "Unsupported format. Use VCF/VCF.GZ or a complete PLINK dataset."
    elif not nonempty: message = "The uploaded file is empty."
    elif not build_ok: message = "Genome build must be GRCh37 or pass a validated harmonization/liftover workflow."
    else: message = "Format and declared build are compatible. Full variant, allele, sample, and coverage QC is still required before scoring."
    return UploadReport(ready,message,filename,genome_build,{"supported_format":supported,"nonempty":nonempty,"grch37":build_ok})

def build_audit_record(case_ref, z_score, coverage, ancestry, genome_build, source, result, clinical):
    return {"generated":date.today().isoformat(),"case_reference":case_ref,"model":MODEL,"inputs":{"z_score":z_score,"variant_coverage":coverage,"reference_match":ancestry,"genome_build":genome_build,"score_source":source,"clinical_context":clinical},"result":result.to_dict(),"limitations":"Research interpretation only; not validated for diagnosis or Pakistani clinical deployment."}

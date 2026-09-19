import math
from pgs_engine import MODEL, interpret_score, validate_genotype_upload

def test_mean_score():
    r=interpret_score(0,100,"South Asian","GRCh37","PGS Catalog pipeline"); assert r.percentile==50.0 and r.relative_odds==1.0 and r.quality_score==100
def test_one_sd_effect():
    r=interpret_score(1,100,"South Asian","GRCh37","PGS Catalog pipeline"); assert math.isclose(r.relative_odds,MODEL["or_per_sd"],rel_tol=.02)
def test_low_coverage():
    assert interpret_score(0,70,"South Asian","GRCh37","PGS Catalog pipeline").quality_score < interpret_score(0,100,"South Asian","GRCh37","PGS Catalog pipeline").quality_score
def test_population_mismatch():
    r=interpret_score(0,100,"Mixed/other","GRCh37","PGS Catalog pipeline"); assert r.quality_score==75
def test_upload_build():
    assert validate_genotype_upload("sample.vcf.gz",1000,"GRCh37").ready; assert not validate_genotype_upload("sample.vcf.gz",1000,"GRCh38").ready
def test_upload_format():
    assert not validate_genotype_upload("sample.csv",1000,"GRCh37").ready

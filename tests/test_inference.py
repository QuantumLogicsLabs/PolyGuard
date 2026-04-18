"""
tests/test_inference.py
=======================
Integration tests for the inference pipeline (rules-only mode, no GPU required).
"""
import pytest
from src.inference.pipeline import PolyGuardPipeline, AnalysisResult


@pytest.fixture
def pipeline():
    """Rules-only pipeline — no model file required."""
    return PolyGuardPipeline.rules_only()


def test_pipeline_returns_analysis_result(pipeline):
    result = pipeline.analyze("x = 1", language="python")
    assert isinstance(result, AnalysisResult)


def test_pipeline_detects_sqli(pipeline):
    code = 'cursor.execute("SELECT * FROM users WHERE id = " + uid)'
    result = pipeline.analyze(code, language="python")
    types = [f.vuln_type for f in result.findings]
    assert "sql_injection" in types


def test_pipeline_detects_xss(pipeline):
    code = "div.innerHTML = req.query.name;"
    result = pipeline.analyze(code, language="javascript")
    types = [f.vuln_type for f in result.findings]
    assert "xss" in types


def test_pipeline_detects_secret(pipeline):
    code = 'api_key = "sk-verysecretkey12345678"'
    result = pipeline.analyze(code, language="python")
    types = [f.vuln_type for f in result.findings]
    assert "hardcoded_secret" in types


def test_clean_code_no_findings(pipeline):
    code = "def add(a, b):\n    return a + b"
    result = pipeline.analyze(code, language="python")
    assert len(result.findings) == 0


def test_overall_risk_critical_for_sqli(pipeline):
    code = 'cursor.execute("SELECT * FROM users WHERE id = " + uid)'
    result = pipeline.analyze(code, language="python")
    assert result.overall_risk == "Critical"


def test_overall_risk_low_for_clean(pipeline):
    code = "print('hello world')"
    result = pipeline.analyze(code, language="python")
    assert result.overall_risk == "Low"


def test_scan_time_recorded(pipeline):
    result = pipeline.analyze("x = 1", language="python")
    assert result.scan_time_ms >= 0


def test_summary_string(pipeline):
    code = 'cursor.execute("SELECT * FROM t WHERE id = " + uid)'
    result = pipeline.analyze(code, language="python")
    summary = result.summary()
    assert "finding" in summary.lower()


def test_multi_vuln_code(pipeline):
    code = (
        'api_key = "sk-supersecretkey12345678"\n'
        'cursor.execute("SELECT * FROM t WHERE id = " + uid)\n'
        "hashlib.md5(data)\n"
    )
    result = pipeline.analyze(code, language="python")
    types = {f.vuln_type for f in result.findings}
    assert "sql_injection" in types
    assert "hardcoded_secret" in types
    assert "weak_crypto" in types

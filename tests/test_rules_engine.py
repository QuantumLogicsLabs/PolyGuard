"""
tests/test_rules_engine.py
==========================
Unit tests for the static analysis rules engine.
"""
import pytest
from src.rules_engine.rules_engine import run_rules


# ── SQL Injection ─────────────────────────────────────────────────────────────

def test_sqli_detected_string_concat_python():
    code = 'cursor.execute("SELECT * FROM users WHERE id = " + user_id)'
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "sql_injection" in types


def test_sqli_detected_fstring():
    code = 'cursor.execute(f"SELECT * FROM users WHERE name = {name}")'
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "sql_injection" in types


def test_sqli_clean_parameterized():
    code = 'cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))'
    findings = run_rules(code, "python")
    sqli = [f for f in findings if f.vuln_type == "sql_injection"]
    assert len(sqli) == 0


# ── XSS ───────────────────────────────────────────────────────────────────────

def test_xss_innerhtml_variable():
    code = "element.innerHTML = userInput;"
    findings = run_rules(code, "javascript")
    types = [f.vuln_type for f in findings]
    assert "xss" in types


def test_xss_safe_textcontent():
    code = "element.textContent = userInput;"
    findings = run_rules(code, "javascript")
    xss = [f for f in findings if f.vuln_type == "xss"]
    assert len(xss) == 0


def test_xss_not_triggered_for_python():
    code = "element.innerHTML = userInput;"
    findings = run_rules(code, "python")
    xss = [f for f in findings if f.vuln_type == "xss"]
    assert len(xss) == 0


# ── Memory Safety ─────────────────────────────────────────────────────────────

def test_strcpy_detected():
    code = "strcpy(buf, argv[1]);"
    findings = run_rules(code, "cpp")
    types = [f.vuln_type for f in findings]
    assert "buffer_overflow" in types


def test_gets_detected():
    code = "gets(buffer);"
    findings = run_rules(code, "c")
    types = [f.vuln_type for f in findings]
    assert "buffer_overflow" in types


def test_memory_not_triggered_for_python():
    code = "strcpy(buf, argv[1]);"
    findings = run_rules(code, "python")
    mem = [f for f in findings if f.vuln_type == "buffer_overflow"]
    assert len(mem) == 0


# ── Secrets ───────────────────────────────────────────────────────────────────

def test_hardcoded_api_key():
    code = 'api_key = "sk-abc123supersecretvalue"'
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "hardcoded_secret" in types


def test_hardcoded_password():
    code = 'password = "hunter2"'
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "hardcoded_secret" in types


def test_aws_key_detected():
    code = "const key = 'AKIAIOSFODNN7EXAMPLE';"
    findings = run_rules(code, "javascript")
    types = [f.vuln_type for f in findings]
    assert "hardcoded_secret" in types


# ── Weak Crypto ───────────────────────────────────────────────────────────────

def test_md5_detected():
    code = "import hashlib\nhash = hashlib.md5(data).hexdigest()"
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "weak_crypto" in types


def test_sha1_detected():
    code = "hashlib.sha1(b'data').hexdigest()"
    findings = run_rules(code, "python")
    types = [f.vuln_type for f in findings]
    assert "weak_crypto" in types


# ── Finding structure ─────────────────────────────────────────────────────────

def test_finding_has_required_fields():
    code = 'cursor.execute("SELECT * FROM t WHERE id = " + uid)'
    findings = run_rules(code, "python")
    assert len(findings) > 0
    f = findings[0]
    assert f.vuln_type
    assert f.severity in ("Low", "Medium", "High", "Critical")
    assert isinstance(f.line, int)
    assert isinstance(f.confidence, float)
    assert f.suggested_fix


def test_findings_sorted_by_line():
    code = (
        'api_key = "sk-supersecretvalue123abc"\n'
        'cursor.execute("SELECT * FROM t WHERE id = " + uid)\n'
    )
    findings = run_rules(code, "python")
    lines = [f.line for f in findings]
    assert lines == sorted(lines)

"""
sqli_detector.py
================
Regex-based SQL Injection detector.
"""
import re
from typing import List

from .base_detector import BaseDetector, RuleFinding

# Patterns that suggest string concatenation into SQL
_SQLI_PATTERNS = [
    # Python: cursor.execute("... " + var)
    re.compile(
        r'execute\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE|DROP).*?["\']'
        r'\s*\+',
        re.IGNORECASE,
    ),
    # Python f-string SQL
    re.compile(
        r'execute\s*\(\s*f["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?\{',
        re.IGNORECASE,
    ),
    # Python % format SQL
    re.compile(
        r'execute\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?%\s*\w',
        re.IGNORECASE,
    ),
    # JS: db.query("SELECT ... " + var)
    re.compile(
        r'\.query\s*\(\s*["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?["\']'
        r'\s*\+',
        re.IGNORECASE,
    ),
    # JS template literals
    re.compile(
        r'\.query\s*\(\s*`.*?(SELECT|INSERT|UPDATE|DELETE).*?\$\{',
        re.IGNORECASE,
    ),
]

_FIX = (
    "Use parameterized queries / prepared statements. "
    "Pass user data as bound parameters, never concatenate it into the SQL string."
)


class SQLiDetector(BaseDetector):
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        findings: List[RuleFinding] = []
        for pattern in _SQLI_PATTERNS:
            for match in pattern.finditer(code):
                line, col = self._get_line_col(code, match)
                findings.append(
                    RuleFinding(
                        vuln_type="sql_injection",
                        severity="Critical",
                        line=line,
                        column=col,
                        snippet=match.group(0)[:120],
                        message="Possible SQL Injection: user-controlled data concatenated into SQL query.",
                        cwe="CWE-89",
                        confidence=0.85,
                        suggested_fix=_FIX,
                    )
                )
        return findings

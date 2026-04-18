"""
memory_safety_detector.py
=========================
Detects common C/C++ memory safety issues.
"""
import re
from typing import List

from .base_detector import BaseDetector, RuleFinding

_MEM_PATTERNS = [
    (
        re.compile(r'\bstrcpy\s*\(', re.IGNORECASE),
        "Use of unsafe strcpy() — consider strncpy() or strlcpy().",
        "buffer_overflow",
        "Critical",
        "CWE-120",
        "Replace strcpy() with strncpy(dest, src, sizeof(dest) - 1) and ensure null termination.",
    ),
    (
        re.compile(r'\bsprintf\s*\(', re.IGNORECASE),
        "Use of unsafe sprintf() — consider snprintf().",
        "buffer_overflow",
        "High",
        "CWE-120",
        "Replace sprintf() with snprintf(buf, sizeof(buf), ...).",
    ),
    (
        re.compile(r'\bgets\s*\(', re.IGNORECASE),
        "Use of dangerous gets() — always causes buffer overflow.",
        "buffer_overflow",
        "Critical",
        "CWE-242",
        "Replace gets() with fgets(buf, sizeof(buf), stdin).",
    ),
    (
        re.compile(r'malloc\s*\([^)]+\)\s*;(?!\s*(if|NULL))', re.IGNORECASE),
        "malloc() return value not checked for NULL.",
        "buffer_overflow",
        "Medium",
        "CWE-476",
        "Always check if malloc() returned NULL before using the pointer.",
    ),
]


class MemorySafetyDetector(BaseDetector):
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        if language not in ("cpp", "c"):
            return []
        findings: List[RuleFinding] = []
        for pattern, message, vuln_type, severity, cwe, fix in _MEM_PATTERNS:
            for match in pattern.finditer(code):
                line, col = self._get_line_col(code, match)
                findings.append(
                    RuleFinding(
                        vuln_type=vuln_type,
                        severity=severity,
                        line=line,
                        column=col,
                        snippet=match.group(0)[:80],
                        message=message,
                        cwe=cwe,
                        confidence=0.90,
                        suggested_fix=fix,
                    )
                )
        return findings

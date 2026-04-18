"""
xss_detector.py
===============
Regex-based Cross-Site Scripting (XSS) detector.
"""
import re
from typing import List

from .base_detector import BaseDetector, RuleFinding

_XSS_PATTERNS = [
    # innerHTML / outerHTML assignment with variable
    re.compile(r'\.(innerHTML|outerHTML)\s*[+]?=\s*(?!["\'`])', re.IGNORECASE),
    # document.write with variable
    re.compile(r'document\.write\s*\(\s*(?!["\'])', re.IGNORECASE),
    # jQuery .html() with variable
    re.compile(r'\$\([^)]+\)\.html\s*\(\s*(?!["\'])', re.IGNORECASE),
    # React dangerouslySetInnerHTML
    re.compile(r'dangerouslySetInnerHTML\s*=\s*\{\s*\{', re.IGNORECASE),
]

_FIX = (
    "Sanitize user input before inserting into the DOM. "
    "Use textContent instead of innerHTML, or a library like DOMPurify."
)


class XSSDetector(BaseDetector):
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        if language not in ("javascript", "typescript", "html"):
            return []
        findings: List[RuleFinding] = []
        for pattern in _XSS_PATTERNS:
            for match in pattern.finditer(code):
                line, col = self._get_line_col(code, match)
                findings.append(
                    RuleFinding(
                        vuln_type="xss",
                        severity="High",
                        line=line,
                        column=col,
                        snippet=match.group(0)[:120],
                        message="Possible XSS: unsanitized data written to DOM.",
                        cwe="CWE-79",
                        confidence=0.80,
                        suggested_fix=_FIX,
                    )
                )
        return findings

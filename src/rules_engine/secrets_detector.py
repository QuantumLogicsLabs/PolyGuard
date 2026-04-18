"""
secrets_detector.py
===================
Detects hardcoded secrets, API keys, and credentials.
"""
import re
from typing import List

from .base_detector import BaseDetector, RuleFinding

_SECRET_PATTERNS = [
    (
        re.compile(
            r'(api_key|apikey|api_secret|secret_key|private_key|auth_token|access_token)'
            r'\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']',
            re.IGNORECASE,
        ),
        "Hardcoded API key or secret token detected.",
    ),
    (
        re.compile(
            r'(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']',
            re.IGNORECASE,
        ),
        "Hardcoded password detected.",
    ),
    (
        re.compile(r'sk-[a-zA-Z0-9]{20,}'),
        "Possible OpenAI API key detected.",
    ),
    (
        re.compile(r'AKIA[0-9A-Z]{16}'),
        "Possible AWS Access Key ID detected.",
    ),
    (
        re.compile(r'ghp_[a-zA-Z0-9]{36}'),
        "Possible GitHub Personal Access Token detected.",
    ),
    (
        re.compile(r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----'),
        "Private key material embedded in source code.",
    ),
]

_FIX = (
    "Never hardcode secrets in source code. "
    "Use environment variables (os.environ), a secrets manager (AWS Secrets Manager, "
    "HashiCorp Vault), or a .env file excluded from version control."
)


class SecretsDetector(BaseDetector):
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        findings: List[RuleFinding] = []
        for pattern, message in _SECRET_PATTERNS:
            for match in pattern.finditer(code):
                line, col = self._get_line_col(code, match)
                findings.append(
                    RuleFinding(
                        vuln_type="hardcoded_secret",
                        severity="High",
                        line=line,
                        column=col,
                        snippet=match.group(0)[:80],
                        message=message,
                        cwe="CWE-798",
                        confidence=0.92,
                        suggested_fix=_FIX,
                    )
                )
        return findings

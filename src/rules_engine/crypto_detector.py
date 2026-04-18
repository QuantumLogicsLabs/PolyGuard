"""
crypto_detector.py
==================
Detects use of weak or broken cryptographic algorithms.
"""
import re
from typing import List

from .base_detector import BaseDetector, RuleFinding

_CRYPTO_PATTERNS = [
    (
        re.compile(r'\bhashlib\.md5\b', re.IGNORECASE),
        "Use of MD5 hash — cryptographically broken.",
        "Replace hashlib.md5 with hashlib.sha256 or hashlib.sha3_256.",
    ),
    (
        re.compile(r'\bhashlib\.sha1\b', re.IGNORECASE),
        "Use of SHA-1 hash — deprecated for security use.",
        "Replace hashlib.sha1 with hashlib.sha256 or better.",
    ),
    (
        re.compile(r'\bDES\b|\bRC4\b|\bRC2\b', re.IGNORECASE),
        "Use of broken symmetric cipher (DES/RC4/RC2).",
        "Use AES-256-GCM or ChaCha20-Poly1305 instead.",
    ),
    (
        re.compile(r'CryptoJS\.MD5|CryptoJS\.SHA1', re.IGNORECASE),
        "JavaScript: use of weak hash via CryptoJS.",
        "Use CryptoJS.SHA256 or the Web Crypto API with SHA-256.",
    ),
    (
        re.compile(r'\brandom\.random\(\)|Math\.random\(\)', re.IGNORECASE),
        "Use of non-cryptographic RNG for potentially security-sensitive context.",
        "Use secrets.token_bytes() (Python) or crypto.getRandomValues() (JS) for security-sensitive randomness.",
    ),
]


class CryptoDetector(BaseDetector):
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        findings: List[RuleFinding] = []
        for pattern, message, fix in _CRYPTO_PATTERNS:
            for match in pattern.finditer(code):
                line, col = self._get_line_col(code, match)
                findings.append(
                    RuleFinding(
                        vuln_type="weak_crypto",
                        severity="Medium",
                        line=line,
                        column=col,
                        snippet=match.group(0)[:80],
                        message=message,
                        cwe="CWE-327",
                        confidence=0.88,
                        suggested_fix=fix,
                    )
                )
        return findings

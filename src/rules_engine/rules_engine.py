"""
rules_engine.py
===============
Orchestrates all rule-based detectors. Returns a unified list of findings.
"""
from typing import List

from .base_detector import RuleFinding
from .sqli_detector import SQLiDetector
from .xss_detector import XSSDetector
from .memory_safety_detector import MemorySafetyDetector
from .secrets_detector import SecretsDetector
from .crypto_detector import CryptoDetector
from src.utils import get_logger

logger = get_logger(__name__)

_DETECTORS = [
    SQLiDetector(),
    XSSDetector(),
    MemorySafetyDetector(),
    SecretsDetector(),
    CryptoDetector(),
]


def run_rules(code: str, language: str) -> List[RuleFinding]:
    """
    Run all rule-based detectors on a code snippet.

    Parameters
    ----------
    code     : source code string
    language : one of 'python', 'javascript', 'cpp', 'c', 'typescript', 'html'

    Returns
    -------
    List of RuleFinding objects, sorted by line number.
    """
    findings: List[RuleFinding] = []
    for detector in _DETECTORS:
        try:
            results = detector.detect(code, language.lower())
            findings.extend(results)
        except Exception as exc:
            logger.warning(f"Detector {detector.__class__.__name__} failed: {exc}")
    findings.sort(key=lambda f: f.line)
    logger.debug(f"Rules engine found {len(findings)} issues in {language} snippet")
    return findings

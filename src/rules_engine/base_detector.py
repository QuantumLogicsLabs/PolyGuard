"""
base_detector.py
================
Abstract base class for all rule-based vulnerability detectors.
"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RuleFinding:
    """A single finding from a rule-based detector."""
    vuln_type: str
    severity: str          # Low | Medium | High | Critical
    line: int
    column: int
    snippet: str
    message: str
    cwe: Optional[str] = None
    confidence: float = 0.9
    suggested_fix: Optional[str] = None


class BaseDetector(ABC):
    """Abstract detector — subclass and implement `detect`."""

    @abstractmethod
    def detect(self, code: str, language: str) -> List[RuleFinding]:
        ...

    @staticmethod
    def _get_line_col(code: str, match: re.Match) -> tuple:
        """Return (line_number, column) for a regex match."""
        start = match.start()
        lines = code[:start].split("\n")
        line = len(lines)
        col = len(lines[-1]) + 1
        return line, col

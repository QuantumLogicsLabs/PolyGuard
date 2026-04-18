"""
pipeline.py
===========
PolyGuard's public inference API.

    from src.inference.pipeline import PolyGuardPipeline

    pipeline = PolyGuardPipeline.from_pretrained("models_saved/best_model.pt")
    results  = pipeline.analyze(code, language="python")
    for f in results.findings:
        print(f"[{f.severity}] {f.vuln_type} at line {f.line}")
        print(f"  {f.message}")
        print(f"  Fix: {f.suggested_fix}")
        print(f"  Confidence: {f.confidence:.0%}")
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import torch

from src.data_pipeline.tokenizer import tokenize_code
from src.data_pipeline.code_dataset import LABEL_NAMES
from src.models.codebert_classifier import CodeBERTClassifier
from src.rules_engine.rules_engine import run_rules
from src.rules_engine.base_detector import RuleFinding
from src.utils import get_logger, load_model_config

logger = get_logger(__name__)

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


@dataclass
class Finding:
    """A unified finding from either the ML model or the rules engine."""
    vuln_type: str
    severity: str
    line: int
    column: int
    snippet: str
    message: str
    cwe: Optional[str]
    confidence: float
    suggested_fix: Optional[str]
    source: str  # "ml" | "rules" | "fusion"


@dataclass
class AnalysisResult:
    language: str
    findings: List[Finding] = field(default_factory=list)
    overall_risk: str = "Low"
    scan_time_ms: float = 0.0

    def summary(self) -> str:
        counts = {}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        parts = [f"{v}×{k}" for k, v in sorted(counts.items(), key=lambda x: -SEVERITY_ORDER[x[0]])]
        return f"{len(self.findings)} finding(s): {', '.join(parts) if parts else 'none'}"


class PolyGuardPipeline:
    """
    Hybrid vulnerability scanner:
        1. Rules engine (fast, zero-shot, high precision on known patterns)
        2. ML classifier (CodeBERT fine-tuned, catches semantic issues)
        3. Fusion: deduplicate & merge confidence scores
    """

    def __init__(
        self,
        model: Optional[CodeBERTClassifier],
        threshold: float = 0.5,
        device: str = "cpu",
    ):
        self.model = model
        self.threshold = threshold
        self.device = torch.device(device if torch.cuda.is_available() or device == "cpu" else "cpu")
        if self.model:
            self.model.to(self.device)
            self.model.eval()

    # ── Constructors ──────────────────────────────────────────────────────────

    @classmethod
    def from_pretrained(
        cls,
        model_path: str,
        threshold: float = 0.5,
        device: str = "auto",
    ) -> "PolyGuardPipeline":
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        cfg = load_model_config()
        if Path(model_path).exists():
            logger.info(f"Loading ML model from {model_path}")
            model = CodeBERTClassifier.load(
                model_path,
                model_name=cfg["model"]["base_model"],
                num_labels=cfg["model"]["num_labels"],
            )
        else:
            logger.warning(
                f"Model not found at {model_path}. Running in rules-only mode."
            )
            model = None
        return cls(model=model, threshold=threshold, device=device)

    @classmethod
    def rules_only(cls) -> "PolyGuardPipeline":
        """Create a pipeline that uses only the rules engine (no ML model needed)."""
        return cls(model=None)

    # ── Main API ──────────────────────────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        import time
        t0 = time.perf_counter()

        findings: List[Finding] = []

        # Step 1: Rules engine
        rule_findings = run_rules(code, language)
        for rf in rule_findings:
            findings.append(
                Finding(
                    vuln_type=rf.vuln_type,
                    severity=rf.severity,
                    line=rf.line,
                    column=rf.column,
                    snippet=rf.snippet,
                    message=rf.message,
                    cwe=rf.cwe,
                    confidence=rf.confidence,
                    suggested_fix=rf.suggested_fix,
                    source="rules",
                )
            )

        # Step 2: ML model (if available)
        if self.model is not None:
            ml_findings = self._ml_scan(code, language)
            findings = self._fuse(findings, ml_findings)

        # Step 3: Sort and compute risk
        findings.sort(key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.line))
        overall_risk = self._compute_risk(findings)

        elapsed = (time.perf_counter() - t0) * 1000
        return AnalysisResult(
            language=language,
            findings=findings,
            overall_risk=overall_risk,
            scan_time_ms=round(elapsed, 2),
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _ml_scan(self, code: str, language: str) -> List[Finding]:
        """Run the ML classifier and return label-level findings."""
        cfg = load_model_config()
        encoding = tokenize_code(code, max_length=cfg["model"]["max_seq_length"])
        input_ids      = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            out = self.model(input_ids=input_ids, attention_mask=attention_mask)

        probs = out["probs"].squeeze(0).cpu().tolist()
        findings = []
        for label, prob in zip(LABEL_NAMES, probs):
            if prob >= self.threshold:
                meta = _LABEL_META[label]
                findings.append(
                    Finding(
                        vuln_type=label,
                        severity=meta["severity"],
                        line=0,  # ML model is snippet-level, not line-level
                        column=0,
                        snippet=code[:120],
                        message=meta["message"],
                        cwe=meta["cwe"],
                        confidence=round(prob, 4),
                        suggested_fix=meta["fix"],
                        source="ml",
                    )
                )
        return findings

    @staticmethod
    def _fuse(rule_findings: List[Finding], ml_findings: List[Finding]) -> List[Finding]:
        """
        Merge rule and ML findings.
        If the same vuln_type is flagged by both, boost confidence and mark source='fusion'.
        """
        rule_types = {f.vuln_type for f in rule_findings}
        fused = list(rule_findings)
        for ml_f in ml_findings:
            if ml_f.vuln_type in rule_types:
                # Boost confidence on existing rule finding
                for rf in fused:
                    if rf.vuln_type == ml_f.vuln_type:
                        rf.confidence = min(1.0, (rf.confidence + ml_f.confidence) / 2 + 0.05)
                        rf.source = "fusion"
            else:
                fused.append(ml_f)
        return fused

    @staticmethod
    def _compute_risk(findings: List[Finding]) -> str:
        if not findings:
            return "Low"
        max_sev = max(SEVERITY_ORDER.get(f.severity, 1) for f in findings)
        return {4: "Critical", 3: "High", 2: "Medium", 1: "Low"}.get(max_sev, "Low")


# ── Label metadata for ML output ─────────────────────────────────────────────

_LABEL_META = {
    "sql_injection": {
        "severity": "Critical",
        "cwe": "CWE-89",
        "message": "ML model detected potential SQL Injection pattern.",
        "fix": "Use parameterized queries or an ORM.",
    },
    "xss": {
        "severity": "High",
        "cwe": "CWE-79",
        "message": "ML model detected potential Cross-Site Scripting.",
        "fix": "Sanitize and escape output before rendering in browser.",
    },
    "buffer_overflow": {
        "severity": "Critical",
        "cwe": "CWE-120",
        "message": "ML model detected potential buffer overflow pattern.",
        "fix": "Use safe string functions with explicit size bounds.",
    },
    "hardcoded_secret": {
        "severity": "High",
        "cwe": "CWE-798",
        "message": "ML model detected possible hardcoded credentials.",
        "fix": "Move secrets to environment variables or a secrets manager.",
    },
    "weak_crypto": {
        "severity": "Medium",
        "cwe": "CWE-327",
        "message": "ML model detected weak cryptographic usage.",
        "fix": "Use SHA-256/SHA-3 for hashing; AES-GCM for encryption.",
    },
    "broken_auth": {
        "severity": "High",
        "cwe": "CWE-287",
        "message": "ML model detected broken authentication pattern.",
        "fix": "Use a battle-tested auth library; never roll your own auth.",
    },
}

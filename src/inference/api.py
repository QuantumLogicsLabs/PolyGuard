"""
api.py
======
FastAPI REST backend for PolyGuard.

Run with:
    uvicorn src.inference.api:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.inference.pipeline import PolyGuardPipeline, Finding
from src.utils import get_logger

logger = get_logger(__name__)

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PolyGuard API",
    description="AI-Powered Code Security Analyzer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pipeline singleton ────────────────────────────────────────────────────────
_pipeline: Optional[PolyGuardPipeline] = None


def get_pipeline() -> PolyGuardPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PolyGuardPipeline.from_pretrained("models_saved/best_model.pt")
    return _pipeline


# ── Request / Response schemas ────────────────────────────────────────────────

class ScanRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to analyze")
    language: str = Field("python", description="Language: python | javascript | cpp | c")


class FindingOut(BaseModel):
    vuln_type: str
    severity: str
    line: int
    column: int
    snippet: str
    message: str
    cwe: Optional[str]
    confidence: float
    suggested_fix: Optional[str]
    source: str


class ScanResponse(BaseModel):
    language: str
    overall_risk: str
    finding_count: int
    scan_time_ms: float
    findings: List[FindingOut]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    try:
        pipeline = get_pipeline()
        result = pipeline.analyze(req.code, language=req.language)
    except Exception as e:
        logger.error(f"Scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return ScanResponse(
        language=result.language,
        overall_risk=result.overall_risk,
        finding_count=len(result.findings),
        scan_time_ms=result.scan_time_ms,
        findings=[
            FindingOut(
                vuln_type=f.vuln_type,
                severity=f.severity,
                line=f.line,
                column=f.column,
                snippet=f.snippet,
                message=f.message,
                cwe=f.cwe,
                confidence=f.confidence,
                suggested_fix=f.suggested_fix,
                source=f.source,
            )
            for f in result.findings
        ],
    )


@app.post("/scan/rules-only", response_model=ScanResponse)
def scan_rules_only(req: ScanRequest):
    """Faster endpoint: skips ML model, runs rules engine only."""
    try:
        pipeline = PolyGuardPipeline.rules_only()
        result = pipeline.analyze(req.code, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ScanResponse(
        language=result.language,
        overall_risk=result.overall_risk,
        finding_count=len(result.findings),
        scan_time_ms=result.scan_time_ms,
        findings=[
            FindingOut(**{k: getattr(f, k) for k in FindingOut.model_fields})
            for f in result.findings
        ],
    )

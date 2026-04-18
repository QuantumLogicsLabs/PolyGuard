#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_inference.sh  —  Scan a single file for vulnerabilities
#
# Usage:
#   bash scripts/run_inference.sh --input path/to/code.py
#   bash scripts/run_inference.sh --input path/to/code.js --language javascript
#   bash scripts/run_inference.sh --input path/to/code.cpp --rules-only
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

INPUT=""
LANGUAGE="python"
RULES_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input)      INPUT="$2";    shift 2 ;;
        --language)   LANGUAGE="$2"; shift 2 ;;
        --rules-only) RULES_ONLY=true; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [ -z "$INPUT" ]; then
    echo "Usage: bash scripts/run_inference.sh --input <file> [--language <lang>] [--rules-only]"
    exit 1
fi

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Scanning: $INPUT"
echo "═══════════════════════════════════════════════"

python - <<PYEOF
from src.inference.pipeline import PolyGuardPipeline

rules_only = $( [ "$RULES_ONLY" = true ] && echo "True" || echo "False" )
lang = "$LANGUAGE"

with open("$INPUT", "r") as f:
    code = f.read()

if rules_only:
    pipeline = PolyGuardPipeline.rules_only()
else:
    pipeline = PolyGuardPipeline.from_pretrained("models_saved/best_model.pt")

result = pipeline.analyze(code, language=lang)

print(f"\n📊 Overall Risk : {result.overall_risk}")
print(f"⏱  Scan Time   : {result.scan_time_ms:.1f} ms")
print(f"🔍 {result.summary()}\n")

if not result.findings:
    print("✅  No vulnerabilities detected.")
else:
    for i, f in enumerate(result.findings, 1):
        print(f"[{i}] [{f.severity}] {f.vuln_type.upper()} — Line {f.line} (confidence: {f.confidence:.0%})")
        print(f"     {f.message}")
        if f.cwe:
            print(f"     CWE: {f.cwe}")
        if f.suggested_fix:
            print(f"     Fix: {f.suggested_fix}")
        print()
PYEOF

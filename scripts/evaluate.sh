#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# evaluate.sh  —  Evaluate the trained model on the test split
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Evaluation"
echo "═══════════════════════════════════════════════"

python -m src.evaluation.evaluator

echo ""
echo "✅  Evaluation complete."

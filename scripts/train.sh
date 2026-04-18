#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# train.sh  —  Train the CodeBERT multi-label classifier
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Training (CodeBERT)"
echo "═══════════════════════════════════════════════"

# Ensure processed data exists
if [ ! -f "data/processed/train.json" ]; then
    echo "⚠  Processed data not found — running preprocess first…"
    bash scripts/preprocess.sh
fi

python -m src.training.train

echo ""
echo "✅  Training complete."
echo "    Best model → models_saved/best_model.pt"

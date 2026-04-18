#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# train_baseline.sh  —  Train TF-IDF + LightGBM baseline (Experiment 01)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Baseline Training (TF-IDF + LGB)"
echo "═══════════════════════════════════════════════"

if [ ! -f "data/processed/train.json" ]; then
    echo "⚠  Processed data not found — running preprocess first…"
    bash scripts/preprocess.sh
fi

python -m src.training.train_baseline

echo ""
echo "✅  Baseline training complete."
echo "    Model → models_saved/baseline_tfidf.pkl"

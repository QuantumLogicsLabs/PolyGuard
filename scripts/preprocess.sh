#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# preprocess.sh  —  Build train/val/test splits from raw data
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════"
echo "  PolyGuard — Preprocessing"
echo "═══════════════════════════════════════════════"

python -m src.data_pipeline.dataset_builder

echo ""
echo "✅  Preprocessing complete."
echo "    Output → data/processed/{train,val,test}.json"
